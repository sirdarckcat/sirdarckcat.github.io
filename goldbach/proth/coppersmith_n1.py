#!/usr/bin/env python3
"""Self-contained Coppersmith--Howgrave-Graham F > P^(1/4 + eps) N-1 primality prover & verifier.

Implements Research Pillar 4A Feature F16 (PROJECT.md Interface Contract #4):
  1. Certifies p == 1 (mod F) for EVERY prime divisor p | P via verified prime
     factorization of F, Euler(-1) witness a^((P-1)/2) == -1 (mod P), and
     Pocklington witnesses gcd(a_q^((P-1)/q) - 1, P) == 1 for all odd primes q | F.
  2. Partitions [F + 1, isqrt(P)] into zero-gap contiguous integer slabs
     [M_{j,lo}, M_{j,hi}] in 100% exact Python integer arithmetic.
  3. On each lattice slab, centers y = k - k_mid in [-X, X], builds the exact
     integer Hermite Normal Form basis of {P^(m-i)(y + c)^i} U {y^t(y + c)^m},
     solves LLL via batched PARI/GP qflll(M, 1), verifies the strict integer
     Howgrave-Graham bound ||H(X y)||_1 < M_{j,lo}^m, and extracts all integer
     roots in [-X, X] via a pure-Python zero-float root finder (6-prime modular
     filter + Rolle's Theorem Monotone-Gap Partition + safeguarded integer
     Newton-bisection).
  4. Standalone `--verify <cert.json>` never trusts self-reported `"verdict"`,
     `"coppersmith_bound_verified"`, or `"root_check_passed"` fields, and
     automatically runs live slab-covering qflll when `slabs` is absent or
     tampered, deterministically rejecting 3-factor Carmichael--Euler(-1) and
     2-factor balanced Euler(-1) composites with explicit factor output.

CLI usage:
  python3 goldbach/proth/coppersmith_n1.py --verify <cert.json>
  python3 goldbach/proth/coppersmith_n1.py --prove --P <int> --F <int> [--out <cert.json>]
  python3 goldbach/proth/coppersmith_n1.py --prove --m <int> --n <int> [--F <int>] [--out <cert.json>]
  python3 goldbach/proth/coppersmith_n1.py --prove --from-record <record.json> [--F <int>] [--out <cert.json>]
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

try:
    if os.environ.get("NO_GMPY2"):
        raise ImportError
    import gmpy2  # type: ignore

    def _powmod(b: int, e: int, m: int) -> int:
        return int(gmpy2.powmod(b, e, m))

    def _is_perfect_power(n: int) -> tuple[bool, int]:
        if n < 4:
            return False, 0
        if not bool(gmpy2.is_power(n)):
            return False, 0
        max_k = n.bit_length()
        for k in range(2, max_k + 1):
            r, exact = gmpy2.iroot(n, k)
            if exact:
                return True, int(r)
        return False, 0

except Exception:
    gmpy2 = None

    def _powmod(b: int, e: int, m: int) -> int:
        return pow(b, e, m)

    def _is_perfect_power(n: int) -> tuple[bool, int]:
        if n < 4:
            return False, 0
        max_k = n.bit_length()
        for k in range(2, max_k + 1):
            lo, hi = 2, 1 << ((n.bit_length() + k - 1) // k)
            while lo <= hi:
                mid = (lo + hi) >> 1
                v = mid ** k
                if v == n:
                    return True, mid
                if v < n:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return False, 0


# Small odd primes 3..997 for fast trial GCD
def _build_small_primes(limit: int = 997) -> tuple[list[int], int]:
    ps: list[int] = []
    prod = 1
    for n in range(3, limit + 1, 2):
        if all(n % d != 0 for d in range(3, math.isqrt(n) + 1, 2)):
            ps.append(n)
            prod *= n
    return ps, prod


_SMALL_ODD_PRIMES, _SMALL_ODD_PRIMORIAL = _build_small_primes(997)
_MR64_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
_MOD_ROOT_PRIMES = (251, 257, 263, 269, 271, 277)


def _sha256_dec(x: int) -> str:
    return hashlib.sha256(str(x).encode("ascii")).hexdigest()


def _is_strict_int(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _parse_int_field(val: Any, name: str) -> int:
    if isinstance(val, bool):
        raise ValueError(f"field {name!r} must be int/decimal-str, got bool")
    if isinstance(val, int):
        return int(val)
    if isinstance(val, str):
        s = val.strip()
        if not s or (s[0] in "+-" and not s[1:].isdigit()) or (s[0] not in "+-" and not s.isdigit()):
            raise ValueError(f"field {name!r} is not a valid decimal integer string")
        return int(s)
    raise ValueError(f"field {name!r} has invalid type {type(val).__name__}")


# ---------------------------------------------------------------------------
# Deterministic primality & factorization of F
# ---------------------------------------------------------------------------
def is_prime_deterministic(q: int) -> bool:
    """Unconditionally exact primality check (13-base MR below 2^81, PARI isprime above)."""
    if q < 2:
        return False
    if q == 2 or q == 3:
        return True
    if q % 2 == 0:
        return False
    for p in _SMALL_ODD_PRIMES:
        if q == p:
            return True
        if q % p == 0:
            return False
    # Sorenson--Webster (2017): first 13 primes are deterministic below 3.317e24 > 2^81
    if q < (1 << 81):
        d = q - 1
        s = (d & -d).bit_length() - 1
        d >>= s
        for a in _MR64_BASES:
            if a >= q:
                break
            x = _powmod(a, d, q)
            if x == 1 or x == q - 1:
                continue
            for _ in range(s - 1):
                x = (x * x) % q
                if x == q - 1:
                    break
            else:
                return False
        return True
    # Exact APRCL/ECPP proof via PARI/GP isprime()
    gp_code = f"{{print(isprime({q})); quit;}}\n"
    proc = subprocess.run(
        ["gp", "-q", "-f", "-s", "256M"],
        input=gp_code,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"PARI/GP isprime failed: {proc.stderr.strip()}")
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return bool(lines and lines[-1] == "1")


def factor_odd_certified(n_odd: int) -> list[tuple[int, int]]:
    """Factor positive odd integer n_odd into certified (prime, exp) pairs."""
    if n_odd <= 1:
        return []
    rem = n_odd
    factors: dict[int, int] = {}
    for p in _SMALL_ODD_PRIMES:
        if p * p > rem:
            break
        if rem % p == 0:
            e = 0
            while rem % p == 0:
                rem //= p
                e += 1
            factors[p] = factors.get(p, 0) + e
    if rem > 1:
        if is_prime_deterministic(rem):
            factors[rem] = factors.get(rem, 0) + 1
        else:
            try:
                import sympy  # type: ignore

                sub = sympy.factorint(rem)
                for k, e in sub.items():
                    ki = int(k)
                    if not is_prime_deterministic(ki):
                        raise ValueError(f"factor {ki} failed deterministic primality")
                    factors[ki] = factors.get(ki, 0) + int(e)
            except Exception:
                gp_code = f"{{fa = factor({rem}); for(i=1, matsize(fa)[1], print(fa[i,1], \" \", fa[i,2])); quit;}}\n"
                proc = subprocess.run(
                    ["gp", "-q", "-f", "-s", "256M"],
                    input=gp_code,
                    text=True,
                    capture_output=True,
                    timeout=120,
                    check=False,
                )
                if proc.returncode != 0:
                    raise RuntimeError(f"PARI/GP factor failed: {proc.stderr.strip()}")
                for ln in proc.stdout.splitlines():
                    parts = ln.strip().split()
                    if len(parts) == 2:
                        ki, ei = int(parts[0]), int(parts[1])
                        if not is_prime_deterministic(ki):
                            raise ValueError(f"PARI factor {ki} failed deterministic primality")
                        factors[ki] = factors.get(ki, 0) + ei
    out = sorted(factors.items())
    prod = 1
    for q, e in out:
        prod *= q ** e
    if prod != n_odd:
        raise RuntimeError("incomplete odd factorization of F")
    return out


# ---------------------------------------------------------------------------
# Exact integer polynomial & Hermite Normal Form basis
# ---------------------------------------------------------------------------
def build_hnf_polys(P: int, c_shift: int, m: int, d: int) -> list[list[int]]:
    """Construct exact integer HNF basis polynomials b_tilde[0..d-1] of degree < d.

    Unreduced shift polynomials for f(y) = y + c_shift (mod p_1):
      g_i(y) = P^(m - i) * (y + c_shift)^i       for 0 <= i < m
      g_i(y) = y^(i - m) * (y + c_shift)^m       for m <= i < d
    Every b_tilde[i] is an exact Z-linear combination of g_0..g_i with diagonal
    D_i = P^max(0, m - i) and off-diagonal 0 <= b_tilde[i][j] < D_j (0 for j >= m).
    """
    c = c_shift % P
    diag = [P ** (m - i) if i < m else 1 for i in range(d)]

    # Precompute powers (y + c)^i for 0 <= i <= m
    binom_pows: list[list[int]] = [[1]]
    for i in range(1, m + 1):
        prev = binom_pows[-1]
        cur = [0] * (i + 1)
        for k, v in enumerate(prev):
            cur[k] += v * c
            cur[k + 1] += v
        binom_pows.append(cur)

    basis: list[list[int]] = []
    for i in range(d):
        row = [0] * d
        if i < m:
            scale = diag[i]
            bp = binom_pows[i]
            for k in range(i + 1):
                row[k] = bp[k] * scale
        else:
            shift = i - m
            bp = binom_pows[m]
            for k in range(m + 1):
                row[k + shift] = bp[k]

        # Exact integer top-down row reduction against basis[i-1 .. 0]
        for j in range(i - 1, -1, -1):
            dj = diag[j]
            if dj == 1:
                q = row[j]
            else:
                q = row[j] // dj
            if q != 0:
                bj = basis[j]
                for t in range(j + 1):
                    row[t] -= q * bj[t]
        basis.append(row)
    return basis


def reconstruct_poly_from_u(basis: list[list[int]], u: list[int]) -> list[int]:
    d = len(basis)
    H = [0] * d
    for r, ur in enumerate(u):
        if ur != 0:
            br = basis[r]
            for k in range(r + 1):
                H[k] += ur * br[k]
    return H


def poly_scaled_l1_norm(H: list[int], X: int) -> int:
    total = 0
    x_pow = 1
    for hk in H:
        if hk != 0:
            total += abs(hk) * x_pow
        x_pow *= X
    return total


# ---------------------------------------------------------------------------
# Pure-Python Exact Integer Root Finder (6-Prime Filter + Rolle MGP + Newton-Bisection)
# ---------------------------------------------------------------------------
def _to_fast_poly(H: list[int]) -> list[Any]:
    if gmpy2 is not None:
        return [gmpy2.mpz(c) for c in H]
    return H


def _eval_poly(H: list[Any], x: int) -> int:
    if gmpy2 is not None:
        xm = gmpy2.mpz(x)
        acc = gmpy2.mpz(0)
        for c in reversed(H):
            acc = acc * xm + c
        return int(acc)
    acc_i = 0
    for c in reversed(H):
        acc_i = acc_i * x + c
    return acc_i


def _deriv_poly(H: list[int]) -> list[int]:
    return [i * H[i] for i in range(1, len(H))]


def _eval_interval_horner(
    P: list[int], c_bits: list[int], c_tz: list[int], x: int, K: int
) -> tuple[int, int, int, int, int]:
    """Zero-float certified integer interval Horner evaluation of P(x) and P'(x).

    Returns (f_lo, f_hi, df_lo, df_hi, sx) guaranteeing:
      f_lo * 2^S_tot <= P(x) <= f_hi * 2^S_tot
      df_lo * 2^(S_tot - sx) <= P'(x) <= df_hi * 2^(S_tot - sx)
    for an exact integer S_tot >= deg(P) * sx >= 0.
    """
    D = len(P) - 1
    ax = abs(x)
    bx = ax.bit_length()
    sx = max(0, bx - K)
    x_lo = x >> sx
    x_tz = (ax & -ax).bit_length() - 1
    x_hi = x_lo + (1 if x_tz < sx else 0)

    M = 0
    for k, cb in enumerate(c_bits):
        if cb > 0:
            v = cb + k * bx
            if v > M:
                M = v
    S_tot = max(D * sx, M - (D + 1) * K)

    sig_d = S_tot - D * sx
    cd = P[D]
    f_lo = cd >> sig_d
    f_hi = f_lo + (1 if c_tz[D] < sig_d else 0)
    df_lo = 0
    df_hi = 0

    for k in range(D - 1, -1, -1):
        q1 = df_lo * x_lo
        q2 = df_lo * x_hi
        q3 = df_hi * x_lo
        q4 = df_hi * x_hi
        df_lo = min(q1, q2, q3, q4) + f_lo
        df_hi = max(q1, q2, q3, q4) + f_hi

        ck = P[k]
        if ck == 0:
            ck_lo = 0
            ck_hi = 0
        else:
            sig_k = S_tot - k * sx
            ck_lo = ck >> sig_k
            ck_hi = ck_lo + (1 if c_tz[k] < sig_k else 0)

        p1 = f_lo * x_lo
        p2 = f_lo * x_hi
        p3 = f_hi * x_lo
        p4 = f_hi * x_hi
        f_lo = min(p1, p2, p3, p4) + ck_lo
        f_hi = max(p1, p2, p3, p4) + ck_hi

    return f_lo, f_hi, df_lo, df_hi, sx


def _poly_sign_certified(
    P: list[int], Pf: list[Any], c_bits: list[int], c_tz: list[int], max_cb: int, x: int
) -> int:
    """Return exact sign (-1, 0, +1) of P(x) using certified integer intervals before full eval."""
    if x == 0:
        c0 = P[0]
        return 1 if c0 > 0 else (-1 if c0 < 0 else 0)
    bx = abs(x).bit_length()
    if max_cb + (len(P) - 1) * bx > 2048 and (bx > 192 or max_cb > 192):
        f_lo, f_hi, _, _, _ = _eval_interval_horner(P, c_bits, c_tz, x, 192)
        if f_lo > 0:
            return 1
        if f_hi < 0:
            return -1
    fx = _eval_poly(Pf, x)
    return 1 if fx > 0 else (-1 if fx < 0 else 0)


def _eval_sign_and_newton_cand(
    P: list[int],
    Pf: list[Any],
    dPf: list[Any],
    c_bits: list[int],
    c_tz: list[int],
    max_cb: int,
    x: int,
) -> tuple[int, int, int, int]:
    """Return (sign_fx, f_num, df_den, sx) at integer x where:
      - sign_fx in {-1, 0, +1} is the 100% exact sign of P(x) (0 iff P(x) == 0 over Z!),
      - (f_num << sx) / df_den approximates P(x) / P'(x) with certified sign when df_den != 0.
    """
    if x == 0:
        c0 = P[0]
        sgn = 1 if c0 > 0 else (-1 if c0 < 0 else 0)
        c1 = P[1] if len(P) > 1 else 0
        return sgn, c0, c1, 0

    bx = abs(x).bit_length()
    if max_cb + (len(P) - 1) * bx > 2048 and (bx > 192 or max_cb > 192):
        f_lo, f_hi, df_lo, df_hi, sx = _eval_interval_horner(P, c_bits, c_tz, x, 192)
        if f_lo > 0 or f_hi < 0:
            sgn = 1 if f_lo > 0 else -1
            if df_lo > 0 or df_hi < 0:
                return sgn, f_lo + f_hi, df_lo + df_hi, sx
    fx = _eval_poly(Pf, x)
    if fx == 0:
        return 0, 0, 0, 0
    sgn = 1 if fx > 0 else -1
    dfx = _eval_poly(dPf, x)
    return sgn, fx, dfx, 0


def _newton_cand_from_scaled(
    pt: int, sgn_f: int, f_num: int, df_den: int, sx: int, lo: int, hi: int, sgn_lo: int
) -> tuple[int | None, int]:
    """Compute nearest-integer safeguarded Newton candidate from scaled ratio (f_num << sx) / df_den."""
    if df_den == 0 or sgn_f == 0:
        return None, 0
    go_right = sgn_f == sgn_lo
    if go_right:
        if not ((f_num < 0 and df_den > 0) or (f_num > 0 and df_den < 0)):
            return None, 0
    else:
        if not ((f_num > 0 and df_den > 0) or (f_num < 0 and df_den < 0)):
            return None, 0
    af = abs(f_num) << sx
    ad = abs(df_den)
    step = max(1, (af + (ad >> 1)) // ad)
    cand = (pt + step) if go_right else (pt - step)
    if lo < cand < hi:
        return int(cand), int(step)
    return None, 0


def _find_bracket_unit_or_exact(
    P: list[int],
    dP: list[int],
    a: int,
    b: int,
    fa: int,
    fb: int,
    *,
    Pf_in: list[Any] | None = None,
    dPf_in: list[Any] | None = None,
    c_bits_in: list[int] | None = None,
    c_tz_in: list[int] | None = None,
) -> tuple[int, int, int, int]:
    """Given strictly monotonic P on [a, b] (a < b) with fa * fb < 0 and exact derivative dP = P',
    find integer m in [a, b - 1] such that P(m) * P(m + 1) <= 0.
    Uses Press-et-al. `rtsafe` safeguarded integer Newton-bisection + certified integer intervals.
    """
    if len(P) == 2:
        q_lin, rem_lin = divmod(-P[0], P[1])
        if rem_lin == 0:
            return q_lin, q_lin, 0, 0
        sgn_a = 1 if fa > 0 else -1
        return q_lin, q_lin + 1, sgn_a, -sgn_a

    Pf = Pf_in if Pf_in is not None else _to_fast_poly(P)
    dPf = dPf_in if dPf_in is not None else _to_fast_poly(dP)
    c_bits = c_bits_in if c_bits_in is not None else [abs(c).bit_length() for c in P]
    c_tz = c_tz_in if c_tz_in is not None else [((abs(c) & -abs(c)).bit_length() - 1) if c else 0 for c in P]
    max_cb = max(c_bits, default=0)

    lo, hi = a, b
    sgn_lo = 1 if fa > 0 else -1
    sgn_hi = -sgn_lo
    end_lo_info: tuple[int, int, int] | None = None
    end_hi_info: tuple[int, int, int] | None = None
    last_step = hi - lo
    it = 0

    x = (lo + hi) >> 1
    while hi - lo > 1:
        it += 1
        sgn_x, f_num, df_den, sx = _eval_sign_and_newton_cand(P, Pf, dPf, c_bits, c_tz, max_cb, x)
        if sgn_x == 0:
            return x, x, 0, 0

        if sgn_x == sgn_lo:
            lo = x
            end_lo_info = (f_num, df_den, sx)
            updated_lo = True
        else:
            hi = x
            end_hi_info = (f_num, df_den, sx)
            updated_lo = False

        if hi - lo <= 1:
            break

        nxt: int | None = None
        nxt_step = 0
        if (it & 7) != 0:
            nxt, nxt_step = _newton_cand_from_scaled(x, sgn_x, f_num, df_den, sx, lo, hi, sgn_lo)
            if nxt is None:
                if updated_lo:
                    if end_hi_info is None:
                        _, fn_h, df_h, sx_h = _eval_sign_and_newton_cand(P, Pf, dPf, c_bits, c_tz, max_cb, hi)
                        end_hi_info = (fn_h, df_h, sx_h)
                    nxt, nxt_step = _newton_cand_from_scaled(
                        hi, sgn_hi, end_hi_info[0], end_hi_info[1], end_hi_info[2], lo, hi, sgn_lo
                    )
                else:
                    if end_lo_info is None:
                        _, fn_l, df_l, sx_l = _eval_sign_and_newton_cand(P, Pf, dPf, c_bits, c_tz, max_cb, lo)
                        end_lo_info = (fn_l, df_l, sx_l)
                    nxt, nxt_step = _newton_cand_from_scaled(
                        lo, sgn_lo, end_lo_info[0], end_lo_info[1], end_lo_info[2], lo, hi, sgn_lo
                    )

        if nxt is not None and nxt_step * 2 <= last_step:
            last_step = nxt_step
            x = nxt
            continue

        # Fallback: fixed-origin log-scale binary search until [lo, hi] is within a factor of 4 of origin
        x_fb: int | None = None
        if (hi - lo).bit_length() >= 12:
            dist_a = hi - a
            dist_b = b - lo
            if dist_a <= dist_b:
                la = max(0, (lo - a).bit_length() - 1)
                ua = dist_a.bit_length()
                if ua - la >= 3:
                    cand_a = a + (1 << ((la + ua) >> 1))
                    if lo < cand_a < hi:
                        x_fb = cand_a
            else:
                lb = max(0, (b - hi).bit_length() - 1)
                ub = dist_b.bit_length()
                if ub - lb >= 3:
                    cand_b = b - (1 << ((lb + ub) >> 1))
                    if lo < cand_b < hi:
                        x_fb = cand_b

        if x_fb is not None:
            x = x_fb
            last_step = (hi - lo) >> 4
        else:
            x = (lo + hi) >> 1
            last_step = hi - lo

    return lo, hi, sgn_lo, sgn_hi


def _passes_modular_root_filter(H: list[int], lo: int, hi: int) -> bool:
    """Return False if some small prime q proves H(y) != 0 (mod q) for all y in [lo, hi]."""
    span = hi - lo
    for q in _MOD_ROOT_PRIMES:
        hq = [c % q for c in H]
        if all(c == 0 for c in hq):
            continue
        found = False
        if span < q - 1:
            r0 = lo % q
            for off in range(span + 1):
                u = (r0 + off) % q
                acc = 0
                for c in reversed(hq):
                    acc = (acc * u + c) % q
                if acc == 0:
                    found = True
                    break
        else:
            for u in range(q):
                acc = 0
                for c in reversed(hq):
                    acc = (acc * u + c) % q
                if acc == 0:
                    found = True
                    break
        if not found:
            return False
    return True


def exact_int_roots_in_box(H_in: list[int], lo: int, hi: int) -> list[int]:
    """Find ALL exact integer roots y in [lo, hi] of polynomial H_in(y) = 0.
    Uses 0 floats and 0 approximations; provably complete for all degrees and multiplicities.
    """
    if lo > hi:
        return []
    H = list(H_in)
    while H and H[-1] == 0:
        H.pop()
    if len(H) <= 1:
        return []
    # Factor out exact y^v at y == 0
    roots: set[int] = set()
    v0 = 0
    while v0 < len(H) and H[v0] == 0:
        v0 += 1
    if v0 > 0:
        if lo <= 0 <= hi:
            roots.add(0)
        H = H[v0:]
    if len(H) <= 1:
        return sorted(roots)

    # Remove integer content so H is primitive
    g_cont = functools.reduce(math.gcd, (abs(c) for c in H))
    if g_cont > 1:
        H = [c // g_cont for c in H]

    deg = len(H) - 1
    if deg == 1:
        if (-H[0]) % H[1] == 0:
            r = (-H[0]) // H[1]
            if lo <= r <= hi:
                roots.add(r)
        return sorted(roots)

    if hi - lo <= 64:
        for y in range(lo, hi + 1):
            if _eval_poly(H, y) == 0:
                roots.add(y)
        return sorted(roots)

    if not _passes_modular_root_filter(H, lo, hi):
        return sorted(roots)

    # Build derivative chain: chain[0] = H (deg D), ..., chain[D-1] (deg 1), chain[D] (deg 0)
    chain: list[list[int]] = [H]
    while len(chain[-1]) > 1:
        dpoly = _deriv_poly(chain[-1])
        gc = functools.reduce(math.gcd, (abs(c) for c in dpoly))
        if gc > 1:
            dpoly = [c // gc for c in dpoly]
        chain.append(dpoly)

    # Maintain Monotone-Gap Partition (MGP) splits for chain[level]:
    # On every [s_j, s_{j+1}] with s_{j+1} - s_j >= 2, chain[level]' has NO real roots in (s_j, s_{j+1}).
    # At level = deg - 1 (linear), chain[deg] is constant != 0, so [lo, hi] is already an MGP.
    splits = [lo, 0, hi] if (lo < 0 < hi) else [lo, hi]
    for level in range(deg - 1, 0, -1):
        P = chain[level]          # primitive derivative at `level`
        raw_dP = _deriv_poly(P)   # exact un-divided derivative P'(y) for unit-slope Newton steps
        Pf = _to_fast_poly(P)
        dPf = _to_fast_poly(raw_dP)
        c_bits = [abs(c).bit_length() for c in P]
        c_tz = [((abs(c) & -abs(c)).bit_length() - 1) if c else 0 for c in P]
        max_cb = max(c_bits, default=0)
        new_splits: set[int] = set(splits)
        for j in range(len(splits) - 1):
            s0, s1 = splits[j], splits[j + 1]
            if s1 - s0 < 2:
                continue
            if s1 - s0 == 2:
                new_splits.add(s0 + 1)
                continue
            A, B = s0 + 1, s1 - 1
            f0 = _poly_sign_certified(P, Pf, c_bits, c_tz, max_cb, s0)
            fA = _poly_sign_certified(P, Pf, c_bits, c_tz, max_cb, A)
            fB = _poly_sign_certified(P, Pf, c_bits, c_tz, max_cb, B)
            f1 = _poly_sign_certified(P, Pf, c_bits, c_tz, max_cb, s1)
            if fA == 0:
                new_splits.add(A)
                continue
            if fB == 0:
                new_splits.add(B)
                continue
            if (f0 > 0 and fA < 0) or (f0 < 0 and fA > 0):
                new_splits.add(A)
                continue
            if (fB > 0 and f1 < 0) or (fB < 0 and f1 > 0):
                new_splits.add(B)
                continue
            if (fA > 0 and fB < 0) or (fA < 0 and fB > 0):
                m0, m1, _, _ = _find_bracket_unit_or_exact(
                    P, raw_dP, A, B, fA, fB, Pf_in=Pf, dPf_in=dPf, c_bits_in=c_bits, c_tz_in=c_tz
                )
                new_splits.add(m0)
                if m1 != m0:
                    new_splits.add(m1)
        splits = sorted(new_splits)

    # Extract all integer roots of H = chain[0] using its MGP splits and exact H'(y)
    raw_dH = _deriv_poly(H)
    Hf = _to_fast_poly(H)
    dHf = _to_fast_poly(raw_dH)
    hc_bits = [abs(c).bit_length() for c in H]
    hc_tz = [((abs(c) & -abs(c)).bit_length() - 1) if c else 0 for c in H]
    max_hcb = max(hc_bits, default=0)
    for s in splits:
        if _poly_sign_certified(H, Hf, hc_bits, hc_tz, max_hcb, s) == 0:
            roots.add(s)
    for j in range(len(splits) - 1):
        s0, s1 = splits[j], splits[j + 1]
        if s1 - s0 < 2:
            continue
        if s1 - s0 == 2:
            if _poly_sign_certified(H, Hf, hc_bits, hc_tz, max_hcb, s0 + 1) == 0:
                roots.add(s0 + 1)
            continue
        A, B = s0 + 1, s1 - 1
        fA = _poly_sign_certified(H, Hf, hc_bits, hc_tz, max_hcb, A)
        if fA == 0:
            roots.add(A)
            continue
        fB = _poly_sign_certified(H, Hf, hc_bits, hc_tz, max_hcb, B)
        if fB == 0:
            roots.add(B)
            continue
        if (fA > 0 and fB < 0) or (fA < 0 and fB > 0):
            m0, m1, fm0, fm1 = _find_bracket_unit_or_exact(
                H, raw_dH, A, B, fA, fB, Pf_in=Hf, dPf_in=dHf, c_bits_in=hc_bits, c_tz_in=hc_tz
            )
            if fm0 == 0:
                roots.add(m0)
            elif m1 != m0 and fm1 == 0:
                roots.add(m1)
    return sorted(roots)


# ---------------------------------------------------------------------------
# Contiguous Exact-Integer Slab Planner & Batched PARI/GP qflll Solver
# ---------------------------------------------------------------------------
def _log2_int(x: int) -> float:
    if x <= 1:
        return 0.0
    bl = x.bit_length()
    top = x >> max(0, bl - 53)
    return (bl - 53) + math.log2(top) if bl > 53 else math.log2(x)


def _choose_slab_params(P: int, F: int, M_lo: int, S: int) -> tuple[int, int, int]:
    """Choose (m, d, M_hi) in exact int arithmetic minimizing total LLL cost across [M_lo, S]."""
    log2P = _log2_int(P)
    log2M = _log2_int(M_lo)
    log2S = _log2_int(S)
    log2F = _log2_int(F)
    k_lo = max(1, (M_lo - 1 + F - 1) // F)
    k_max = (S - 1) // F
    log2_k_lo = _log2_int(k_lo)

    best_single: tuple[int, float, int, int] | None = None
    best_step: tuple[float, float, int, int] | None = None
    fallback_best: tuple[float, int, int] | None = None

    max_d_search = 18 if P.bit_length() >= 8000 else 44

    for d in range(3, max_d_search + 1):
        margin_bits = 0.28 * d + 4.5
        for m in range(1, min(d, 23)):
            num = m * log2M - (m * (m + 1) / (2.0 * d)) * log2P - margin_bits
            if num <= 0.5:
                continue
            log2X = num / ((d - 1) / 2.0)
            if fallback_best is None or log2X > fallback_best[0]:
                fallback_best = (log2X, m, d)

            diff = (1.0 + log2X) - log2_k_lo
            if diff > 40.0:
                log2_k_hi = 1.0 + log2X
            elif diff < -40.0:
                log2_k_hi = log2_k_lo
            else:
                log2_k_hi = max(log2_k_lo, 1.0 + log2X) + math.log2(1.0 + 2.0 ** (-abs(diff)))

            est_log2_M_hi = min(log2S, log2F + log2_k_hi)
            delta_bits = est_log2_M_hi - log2M
            if est_log2_M_hi >= log2S - 1e-6:
                cand_single = (d, -log2X, m, d)
                if best_single is None or cand_single < best_single:
                    best_single = cand_single
                break
            if delta_bits >= 0.05:
                cost = ((d ** 4.0) * (m ** 0.5)) / delta_bits
                cand_step = (cost, -log2X, m, d)
                if best_step is None or cand_step < best_step:
                    best_step = cand_step
        if best_single is not None and d >= best_single[0]:
            break

    rem_bits = max(1.0, log2S - log2M)
    if best_single is not None and (
        best_step is None or best_single[0] <= 12 or ((best_single[0] ** 4.0) <= best_step[0] * rem_bits)
    ):
        _, neg_l2x, m_sel, d_sel = best_single
        log2X = -neg_l2x
    elif best_step is not None:
        _, neg_l2x, m_sel, d_sel = best_step
        log2X = -neg_l2x
    elif fallback_best is not None:
        log2X, m_sel, d_sel = fallback_best
    else:
        raise ValueError(
            f"Coppersmith slab budget non-positive at M_lo ({M_lo.bit_length()}b) for P ({P.bit_length()}b)"
        )

    shift_bits = min(P.bit_length(), max(1, int(math.floor(log2X))))
    if shift_bits >= 60:
        mant = int((2.0 ** (log2X - math.floor(log2X))) * 1024.0)
        X_est = max(1, (mant << (shift_bits - 10)))
    else:
        X_est = max(1, int(2.0 ** log2X))

    k_hi_est = min(k_max, k_lo + 2 * X_est)
    M_hi = min(S, (k_hi_est + 1) * F)
    if M_hi < M_lo:
        M_hi = M_lo
    return m_sel, d_sel, M_hi


def plan_slabs(P: int, F: int, k_scan: int = 1000) -> list[dict[str, Any]]:
    """Build exact contiguous integer partition [M_{0,lo}, M_{0,hi}], ..., [M_{s-1,lo}, S] of [F+1, isqrt(P)]."""
    S = math.isqrt(P)
    if S < F + 1:
        return []
    k_scan_eff = max(1, min(int(k_scan), 5000))
    slabs: list[dict[str, Any]] = []

    # Slab 0: direct GCD scan over small multipliers 1 <= k <= k_scan_eff
    M_scan_hi = min(S, (k_scan_eff + 1) * F)
    k0_lo = max(1, (F + F) // F)  # == 1
    k0_hi = (M_scan_hi - 1) // F
    slabs.append(
        {
            "mode": "scan",
            "M_lo": F + 1,
            "M_hi": M_scan_hi,
            "k_lo": k0_lo,
            "k_hi": k0_hi,
            "k_mid": 0,
            "X": max(1, k0_hi),
        }
    )

    M_cur = M_scan_hi + 1
    while M_cur <= S:
        k_lo = max(1, (M_cur - 1 + F - 1) // F)
        k_max = (S - 1) // F
        if k_max - k_lo <= 1000:
            slabs.append(
                {
                    "mode": "scan",
                    "M_lo": M_cur,
                    "M_hi": S,
                    "k_lo": k_lo,
                    "k_hi": k_max,
                    "k_mid": 0,
                    "X": max(1, k_max - k_lo),
                }
            )
            break

        m_sel, d_sel, M_hi = _choose_slab_params(P, F, M_cur, S)
        k_hi = (M_hi - 1) // F
        if k_hi <= k_lo + 64:
            M_hi_scan = min(S, (min(k_max, k_lo + 1000) + 1) * F)
            k_hi_scan = (M_hi_scan - 1) // F
            slabs.append(
                {
                    "mode": "scan",
                    "M_lo": M_cur,
                    "M_hi": M_hi_scan,
                    "k_lo": k_lo,
                    "k_hi": k_hi_scan,
                    "k_mid": 0,
                    "X": max(1, k_hi_scan - k_lo),
                }
            )
            M_cur = M_hi_scan + 1
            continue

        k_mid = (k_lo + k_hi) >> 1
        X = max(1, k_hi - k_mid, k_mid - k_lo)
        slabs.append(
            {
                "mode": "lll",
                "M_lo": M_cur,
                "M_hi": M_hi,
                "k_lo": k_lo,
                "k_hi": k_hi,
                "k_mid": k_mid,
                "X": X,
                "m": m_sel,
                "d": d_sel,
            }
        )
        M_cur = M_hi + 1

    return slabs


def run_batch_gp_lll(P: int, F_inv: int, lll_slabs: list[dict[str, Any]]) -> None:
    """Solve all LLL slabs in a single batched PARI/GP `qflll(M, 1)` subprocess.

    Populates `slab["u"]` and `slab["H"]` in-place, verifying exact integer
    ||H(X y)||_1 < M_lo^m (and auto-retrying with bumped (m, d) if needed).
    """
    if not lll_slabs:
        return

    def _solve_subset(targets: list[dict[str, Any]]) -> None:
        gp_lines = ["{"]
        bases_cache: list[list[list[int]]] = []
        for idx, sl in enumerate(targets):
            m = int(sl["m"])
            d = int(sl["d"])
            k_mid = int(sl["k_mid"])
            X = int(sl["X"])
            c_shift = (F_inv + k_mid) % P
            basis = build_hnf_polys(P, c_shift, m, d)
            bases_cache.append(basis)

            xb = max(0, X.bit_length() - 1)
            pb = max(1, P.bit_length() - 1)
            min_diag_bits = min((m - r) * pb + r * xb if r < m else r * xb for r in range(d))
            s_shift = max(0, min(m * xb, min_diag_bits) - 128)

            # Column r of M holds scaled basis polynomial b_tilde[r](X * y) >> s_shift
            x_pows = [1]
            for _ in range(1, d):
                x_pows.append(x_pows[-1] * X)

            rows_str: list[str] = []
            for k in range(d):
                xk = x_pows[k]
                entries = [str((basis[r][k] * xk) >> s_shift) for r in range(d)]
                rows_str.append(", ".join(entries))
            mat_str = "; ".join(rows_str)
            gp_lines.append(f"M = [{mat_str}];")
            gp_lines.append("U = qflll(M, 1);")
            gp_lines.append(f'print("SLAB_BEGIN {idx} ", matsize(U)[2]);')
            gp_lines.append("for(c=1, min(4, matsize(U)[2]), print(Vec(U[,c])));")
            gp_lines.append(f'print("SLAB_END {idx}");')
        gp_lines.append("quit;")
        gp_lines.append("}\n")
        script = "\n".join(gp_lines)

        proc = subprocess.run(
            ["gp", "-q", "-f", "-s", "512M"],
            input=script,
            text=True,
            capture_output=True,
            timeout=240,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"PARI/GP qflll failed (rc={proc.returncode}): {proc.stderr.strip()}")

        cur_idx: int | None = None
        cand_cols: dict[int, list[list[int]]] = {}
        for raw_ln in proc.stdout.splitlines():
            ln = raw_ln.strip()
            if not ln:
                continue
            if ln.startswith("SLAB_BEGIN "):
                parts = ln.split()
                cur_idx = int(parts[1])
                cand_cols[cur_idx] = []
            elif ln.startswith("SLAB_END "):
                cur_idx = None
            elif cur_idx is not None and ln.startswith("[") and ln.endswith("]"):
                vec = [int(tok.strip()) for tok in ln[1:-1].split(",") if tok.strip()]
                cand_cols[cur_idx].append(vec)

        for idx, sl in enumerate(targets):
            cols = cand_cols.get(idx, [])
            if not cols:
                raise RuntimeError(f"PARI/GP returned no LLL columns for slab {idx}")
            basis = bases_cache[idx]
            X = int(sl["X"])
            best_u: list[int] | None = None
            best_H: list[int] | None = None
            best_l1: int | None = None
            for u in cols:
                if len(u) != int(sl["d"]) or not any(u):
                    continue
                H = reconstruct_poly_from_u(basis, u)
                if not any(H):
                    continue
                l1 = poly_scaled_l1_norm(H, X)
                if best_l1 is None or l1 < best_l1:
                    best_l1 = l1
                    best_u = u
                    best_H = H
            if best_u is None or best_H is None or best_l1 is None:
                raise RuntimeError(f"Zero polynomial returned for slab {idx}")
            sl["u"] = best_u
            sl["H"] = best_H
            sl["l1_norm"] = best_l1

    pending = list(lll_slabs)
    for attempt in range(4):
        _solve_subset(pending)
        retry: list[dict[str, Any]] = []
        for sl in pending:
            bound = int(sl["M_lo"]) ** int(sl["m"])
            if int(sl["l1_norm"]) >= bound:
                sl["m"] = int(sl["m"]) + 1
                sl["d"] = int(sl["d"]) + 2
                retry.append(sl)
        if not retry:
            return
        pending = retry

    raise RuntimeError(
        f"{len(pending)} Coppersmith slab(s) did not satisfy strict ||H(X y)||_1 < M_lo^m after retries"
    )


# ---------------------------------------------------------------------------
# Public Prover & Independent Verifier API (Contract #4)
# ---------------------------------------------------------------------------
def _find_witness_base(P: int, odd_primes_F: list[int], start_base: int | None = None) -> tuple[int, dict[str, int], int]:
    """Find Euler(-1) + Pocklington witness base(s), or return (base, map, factor_or_neg1) on failure."""
    candidates = [start_base] if start_base is not None else [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
    ]
    half = (P - 1) >> 1
    euler_base: int | None = None
    for a in candidates:
        if a is None or a < 2 or a >= P:
            continue
        g = math.gcd(a, P)
        if 1 < g < P:
            return a, {}, g
        x = _powmod(a, half, P)
        if x == P - 1:
            euler_base = a
            break
        if x != 1:
            # Fermat or nontrivial square-root witness proves P composite!
            g2 = math.gcd(x - 1, P)
            if 1 < g2 < P:
                return a, {}, g2
            if _powmod(a, P - 1, P) != 1:
                return a, {}, -1
    if euler_base is None:
        return (start_base or 2), {}, -1

    wmap: dict[str, int] = {}
    for q in odd_primes_F:
        exp_q = (P - 1) // q
        found_q = False
        probe_list = [euler_base] + [b for b in _MR64_BASES if b != euler_base] + list(range(43, 120, 2))
        for aq in probe_list:
            if aq >= P:
                continue
            gq = math.gcd(aq, P)
            if 1 < gq < P:
                return euler_base, wmap, gq
            if _powmod(aq, P - 1, P) != 1:
                return euler_base, wmap, -1
            rem = _powmod(aq, exp_q, P)
            if rem == 1:
                if start_base is not None and aq == start_base and len(probe_list) == 1:
                    break
                continue
            g2 = math.gcd(rem - 1, P)
            if 1 < g2 < P:
                return euler_base, wmap, g2
            if g2 == 1:
                if aq != euler_base:
                    wmap[str(q)] = aq
                found_q = True
                break
        if not found_q:
            return euler_base, wmap, -1

    return euler_base, wmap, 0


def prove(
    P: int | str,
    F: int | str | None = None,
    witness_base: int | None = None,
    k_scan: int = 1000,
    *,
    R: int | str | None = None,
    base: int | None = None,
) -> dict[str, Any]:
    """Construct a Contract #4 Coppersmith--Howgrave-Graham N-1 certificate for P."""
    P_int = _parse_int_field(P, "P")
    wb_req = witness_base if witness_base is not None else base

    if P_int < 3 or P_int % 2 == 0:
        return {
            "P": str(P_int),
            "F": str(F if F is not None else 0),
            "R": str(R if R is not None else 0),
            "witness_base": int(wb_req or 2),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "error": "P must be odd >= 3"},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "COMPOSITE_FACTOR_FOUND" if (P_int > 2 and P_int % 2 == 0) else "INCONCLUSIVE",
            **({"factor": "2"} if (P_int > 2 and P_int % 2 == 0) else {}),
        }

    if F is None:
        v2 = ((P_int - 1) & -(P_int - 1)).bit_length() - 1
        F_int = 1 << v2
    else:
        F_int = _parse_int_field(F, "F")

    if F_int < 2 or (P_int - 1) % F_int != 0:
        R_est = (P_int - 1) // max(1, F_int)
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_est),
            "witness_base": int(wb_req or 2),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "error": "F does not divide P-1"},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "INCONCLUSIVE",
        }

    R_int = (P_int - 1) // F_int
    if R is not None and _parse_int_field(R, "R") != R_int:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R),
            "witness_base": int(wb_req or 2),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "error": "F * R != P - 1"},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "INCONCLUSIVE",
        }

    alpha = _log2_int(F_int) / max(1.0, _log2_int(P_int))

    # Small prime GCD & perfect-power check
    if P_int > 997:
        g_sm = math.gcd(P_int, _SMALL_ODD_PRIMORIAL)
        if 1 < g_sm < P_int:
            for sp in _SMALL_ODD_PRIMES:
                if g_sm % sp == 0:
                    g_sm = sp
                    break
            return {
                "P": str(P_int),
                "F": str(F_int),
                "R": str(R_int),
                "witness_base": int(wb_req or 2),
                "lattice_dim": 1,
                "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "alpha": round(alpha, 6)},
                "coppersmith_bound_verified": False,
                "root_check_passed": False,
                "verdict": "COMPOSITE_FACTOR_FOUND",
                "factor": str(g_sm),
            }
    is_pp, pp_root = _is_perfect_power(P_int)
    if is_pp:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_int),
            "witness_base": int(wb_req or 2),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "alpha": round(alpha, 6)},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "COMPOSITE_FACTOR_FOUND",
            "factor": str(pp_root),
        }

    # Strict F > P^(1/4) bound
    if F_int ** 4 <= P_int:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_int),
            "witness_base": int(wb_req or 2),
            "lattice_dim": 1,
            "lattice_params": {
                "method": "coppersmith_howgrave_graham_slab_cover_v1",
                "alpha": round(alpha, 6),
                "error": "F^4 <= P (violates strict Coppersmith F > P^(1/4) bound)",
            },
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "INCONCLUSIVE",
        }

    # Factor F = 2^v2 * F_odd
    v2 = (F_int & -F_int).bit_length() - 1
    F_odd = F_int >> v2
    odd_facs = factor_odd_certified(F_odd)
    odd_primes = [q for q, _ in odd_facs]

    wb, wmap, status = _find_witness_base(P_int, odd_primes, start_base=wb_req)
    if status > 1:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_int),
            "witness_base": int(wb),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "alpha": round(alpha, 6)},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "COMPOSITE_FACTOR_FOUND",
            "factor": str(status),
        }
    if status < 0:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_int),
            "witness_base": int(wb),
            "lattice_dim": 1,
            "lattice_params": {
                "method": "coppersmith_howgrave_graham_slab_cover_v1",
                "alpha": round(alpha, 6),
                "error": "Euler(-1) / Pocklington witness condition failed",
            },
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "INCONCLUSIVE",
        }

    if F_int * F_int > P_int:
        regime = "POCKLINGTON_F_GT_P_1_2"
    elif F_int ** 3 > P_int:
        regime = "BLS_RANGE_COPPERSMITH_F_GT_P_1_3"
    else:
        regime = "COPPERSMITH_STRICT_F_GT_P_1_4"

    slabs = plan_slabs(P_int, F_int, k_scan=k_scan)
    lll_slabs = [s for s in slabs if s["mode"] == "lll"]
    gf = math.gcd(F_int, P_int)
    if 1 < gf < P_int:
        return {
            "P": str(P_int),
            "F": str(F_int),
            "R": str(R_int),
            "witness_base": int(wb),
            "lattice_dim": 1,
            "lattice_params": {"method": "coppersmith_howgrave_graham_slab_cover_v1", "alpha": round(alpha, 6)},
            "coppersmith_bound_verified": False,
            "root_check_passed": False,
            "verdict": "COMPOSITE_FACTOR_FOUND",
            "factor": str(gf),
        }

    F_inv = pow(F_int, -1, P_int)
    if lll_slabs:
        run_batch_gp_lll(P_int, F_inv, lll_slabs)

    m_max = max((int(s["m"]) for s in lll_slabs), default=1)
    d_max = max((int(s["d"]) for s in lll_slabs), default=1)

    serial_slabs: list[dict[str, Any]] = []
    found_factor: int | None = None

    for sl in slabs:
        if sl["mode"] == "scan":
            serial_slabs.append(
                {
                    "mode": "scan",
                    "M_lo": str(sl["M_lo"]),
                    "M_hi": str(sl["M_hi"]),
                    "k_lo": str(sl["k_lo"]),
                    "k_hi": str(sl["k_hi"]),
                    "k_mid": "0",
                    "X": str(sl["X"]),
                }
            )
            if found_factor is None:
                for k in range(int(sl["k_lo"]), int(sl["k_hi"]) + 1):
                    cand = k * F_int + 1
                    g = math.gcd(cand, P_int)
                    if 1 < g < P_int:
                        found_factor = g
                        break
        else:
            serial_slabs.append(
                {
                    "mode": "lll",
                    "M_lo": str(sl["M_lo"]),
                    "M_hi": str(sl["M_hi"]),
                    "k_lo": str(sl["k_lo"]),
                    "k_hi": str(sl["k_hi"]),
                    "k_mid": str(sl["k_mid"]),
                    "X": str(sl["X"]),
                    "m": int(sl["m"]),
                    "d": int(sl["d"]),
                    "u": [str(u_i) for u_i in sl["u"]],
                }
            )
            if found_factor is None:
                X = int(sl["X"])
                k_mid = int(sl["k_mid"])
                rts = exact_int_roots_in_box(sl["H"], -X, X)
                for rt in rts:
                    k_val = k_mid + rt
                    if k_val >= 1:
                        cand = k_val * F_int + 1
                        g = math.gcd(cand, P_int)
                        if 1 < g < P_int:
                            found_factor = g
                            break

    cert: dict[str, Any] = {
        "P": str(P_int),
        "F": str(F_int),
        "R": str(R_int),
        "witness_base": int(wb),
        "lattice_dim": int(d_max),
        "lattice_params": {
            "method": "coppersmith_howgrave_graham_slab_cover_v1",
            "alpha": round(alpha, 6),
            "regime": regime,
            "m_max": int(m_max),
            "d_max": int(d_max),
            "num_slabs": len(serial_slabs),
            "k_scan": int(k_scan),
            "P_sha256": _sha256_dec(P_int),
            "F_sha256": _sha256_dec(F_int),
            "F_odd_prime_factors": [[str(q), int(e)] for q, e in odd_facs],
            "witness_map": wmap,
            "slabs": serial_slabs,
        },
        "coppersmith_bound_verified": True,
        "root_check_passed": found_factor is None,
        "verdict": "PRIME" if found_factor is None else "COMPOSITE_FACTOR_FOUND",
    }
    if found_factor is not None:
        cert["factor"] = str(found_factor)
    return cert


def _live_factor_or_certify_divisor_interval(P: int, F: int) -> tuple[bool, str, int | None, int]:
    """Run live slab-covering qflll on (P, F) to certify [F+1, isqrt(P)] or recover a factor."""
    gf = math.gcd(F, P)
    if 1 < gf < P:
        return False, f"COMPOSITE_FACTOR_FOUND: factor={gf}", gf, 0
    F_inv = pow(F, -1, P)
    slabs = plan_slabs(P, F, k_scan=1000)
    lll_slabs = [s for s in slabs if s["mode"] == "lll"]
    if lll_slabs:
        run_batch_gp_lll(P, F_inv, lll_slabs)

    for j, sl in enumerate(slabs):
        if sl["mode"] == "scan":
            for k in range(int(sl["k_lo"]), int(sl["k_hi"]) + 1):
                g = math.gcd(k * F + 1, P)
                if 1 < g < P:
                    return False, f"COMPOSITE_FACTOR_FOUND: factor={g} (scan slab {j})", g, len(slabs)
        else:
            M_lo = int(sl["M_lo"])
            m = int(sl["m"])
            X = int(sl["X"])
            k_mid = int(sl["k_mid"])
            H = sl["H"]
            if not any(H) or poly_scaled_l1_norm(H, X) >= M_lo ** m:
                return False, f"Howgrave-Graham L1 bound failed on live slab {j}", None, len(slabs)
            for rt in exact_int_roots_in_box(H, -X, X):
                k_val = k_mid + rt
                if k_val >= 1:
                    g = math.gcd(k_val * F + 1, P)
                    if 1 < g < P:
                        return False, f"COMPOSITE_FACTOR_FOUND: factor={g} (LLL slab {j})", g, len(slabs)
    return True, "PRIME", None, len(slabs)


def verify_cert(cert_or_path: dict[str, Any] | str | Path) -> tuple[bool, str, dict[str, Any]]:
    """Independently verify a Contract #4 certificate without trusting self-reported fields.

    Returns (ok, message, details).
    """
    if isinstance(cert_or_path, (str, Path)):
        p = Path(cert_or_path)
        if not p.is_file():
            return False, f"Certificate file not found: {p}", {"error": "missing_file"}
        try:
            cert = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, f"Invalid JSON certificate: {exc}", {"error": "bad_json"}
    elif isinstance(cert_or_path, dict):
        cert = cert_or_path
    else:
        return False, "Certificate must be dict or path", {"error": "bad_type"}

    if not isinstance(cert, dict):
        return False, "Certificate root must be a JSON object", {"error": "bad_root"}

    req_keys = {
        "P",
        "F",
        "R",
        "witness_base",
        "lattice_dim",
        "lattice_params",
        "coppersmith_bound_verified",
        "root_check_passed",
        "verdict",
    }
    missing = sorted(req_keys - set(cert.keys()))
    if missing:
        return False, f"Missing required Contract #4 keys: {missing}", {"missing": missing}

    if not isinstance(cert["coppersmith_bound_verified"], bool) or not isinstance(cert["root_check_passed"], bool):
        return False, "coppersmith_bound_verified and root_check_passed must be booleans", {}
    if not _is_strict_int(cert["witness_base"]):
        return False, "witness_base must be an integer", {}
    if not _is_strict_int(cert["lattice_dim"]) or int(cert["lattice_dim"]) < 1:
        return False, "lattice_dim must be an integer >= 1", {}
    if not isinstance(cert["lattice_params"], dict):
        return False, "lattice_params must be an object", {}

    metadata_ok = (
        cert["verdict"] == "PRIME"
        and cert["coppersmith_bound_verified"] is True
        and cert["root_check_passed"] is True
    )

    try:
        P = _parse_int_field(cert["P"], "P")
        F = _parse_int_field(cert["F"], "F")
        R = _parse_int_field(cert["R"], "R")
    except Exception as exc:
        return False, f"Integer parse error: {exc}", {}

    wb = int(cert["witness_base"])
    lparams: dict[str, Any] = cert["lattice_params"]

    # Basic arithmetic & algebraic checks
    if P < 3:
        return False, f"P={P} < 3 is not an odd prime", {}
    if P % 2 == 0:
        return False, "COMPOSITE_FACTOR_FOUND: factor=2 (P is even)", {"factor": "2"}
    if F < 2 or R < 1:
        return False, f"Invalid F={F} or R={R}", {}
    if F * R != P - 1:
        return False, "F * R != P - 1", {}

    # Small prime divisors & perfect power check BEFORE F^4 check so trivial composites give factors
    if P > 997:
        g_sm = math.gcd(P, _SMALL_ODD_PRIMORIAL)
        if 1 < g_sm < P:
            for sp in _SMALL_ODD_PRIMES:
                if g_sm % sp == 0:
                    g_sm = sp
                    break
            return False, f"COMPOSITE_FACTOR_FOUND: factor={g_sm} (small prime)", {"factor": str(g_sm)}
    is_pp, pp_root = _is_perfect_power(P)
    if is_pp:
        return False, f"COMPOSITE_FACTOR_FOUND: factor={pp_root} (perfect power)", {"factor": str(pp_root)}

    # Strict Coppersmith exponent bound: F > P^(1/4) <=> F^4 > P
    if F ** 4 <= P:
        return False, f"Under-bound F <= P^(1/4): F^4 <= P (alpha={_log2_int(F)/_log2_int(P):.6f})", {}

    # Certify prime factorization of F = 2^v2 * F_odd
    v2 = (F & -F).bit_length() - 1
    F_odd = F >> v2
    odd_primes: list[int] = []
    if "F_odd_prime_factors" in lparams and lparams["F_odd_prime_factors"] is not None:
        raw_facs = lparams["F_odd_prime_factors"]
        if not isinstance(raw_facs, list):
            return False, "F_odd_prime_factors must be a list", {}
        prod = 1
        seen_q: set[int] = set()
        max_exp = F_odd.bit_length()
        for item in raw_facs:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                return False, "Malformed F_odd_prime_factors entry", {}
            try:
                qi = _parse_int_field(item[0], "q")
                ei = _parse_int_field(item[1], "exp")
            except (ValueError, TypeError) as exc:
                return False, f"Integer parse error in F_odd_prime_factors: {exc}", {}
            if (
                qi < 3
                or (qi & 1) == 0
                or qi > F_odd
                or ei < 1
                or ei > max_exp
                or (qi.bit_length() - 1) * ei > max_exp
                or qi in seen_q
            ):
                return False, f"Invalid/out-of-bounds odd prime factor entry [q, exp] (exp={ei})", {}
            q_pow = qi ** ei
            if F_odd % q_pow != 0:
                return False, f"Claimed prime power q^exp does not divide F_odd (q={qi}, exp={ei})", {}
            if not is_prime_deterministic(qi):
                return False, f"Claimed F factor {qi} is COMPOSITE", {}
            seen_q.add(qi)
            odd_primes.append(qi)
            prod *= q_pow
        if prod != F_odd:
            return False, "Product of F_odd_prime_factors does not equal odd part of F", {}
    elif F_odd > 1:
        try:
            odd_facs = factor_odd_certified(F_odd)
            odd_primes = [q for q, _ in odd_facs]
        except Exception as exc:
            return False, f"Failed to certify prime factorization of F_odd: {exc}", {}

    # Verify Euler(-1) + Pocklington witness obligations
    if wb < 2 or wb >= P:
        return False, f"witness_base={wb} out of range [2, P-1]", {}
    g0 = math.gcd(wb, P)
    if 1 < g0 < P:
        return False, f"COMPOSITE_FACTOR_FOUND: factor={g0} (gcd with witness_base)", {"factor": str(g0)}
    x2 = _powmod(wb, (P - 1) >> 1, P)
    if x2 != P - 1:
        if x2 != 1:
            g2 = math.gcd(x2 - 1, P)
            if 1 < g2 < P:
                return False, f"COMPOSITE_FACTOR_FOUND: factor={g2} (nontrivial sqrt of 1)", {"factor": str(g2)}
        return False, f"Euler(-1) witness check failed for base {wb}: a^((P-1)/2) != -1 (mod P)", {}

    wmap = lparams.get("witness_map", {})
    if not isinstance(wmap, dict):
        return False, "witness_map must be a dict", {}
    for k_w, v_w in wmap.items():
        try:
            _parse_int_field(k_w, "witness_map key")
            _parse_int_field(v_w, f"witness_map[{k_w}]")
        except (ValueError, TypeError) as exc:
            return False, f"Integer parse error in witness_map: {exc}", {}
    by_base: dict[int, list[int]] = {}
    for q in odd_primes:
        try:
            aq = _parse_int_field(wmap.get(str(q), wb), f"witness_map[{q}]")
        except (ValueError, TypeError) as exc:
            return False, f"Integer parse error in witness_map: {exc}", {}
        if aq < 2 or aq >= P:
            return False, f"witness base {aq} for prime {q} out of range", {}
        by_base.setdefault(aq, []).append(q)

    def _cofactor_tree(qs_slice: list[int], cur_val: int) -> list[int]:
        if len(qs_slice) == 1:
            return [cur_val]
        mid = len(qs_slice) >> 1
        left_qs, right_qs = qs_slice[:mid], qs_slice[mid:]
        left_val = _powmod(cur_val, math.prod(right_qs), P)
        right_val = _powmod(cur_val, math.prod(left_qs), P)
        return _cofactor_tree(left_qs, left_val) + _cofactor_tree(right_qs, right_val)

    for aq, qs_list in by_base.items():
        gq = math.gcd(aq, P)
        if 1 < gq < P:
            return False, f"COMPOSITE_FACTOR_FOUND: factor={gq}", {"factor": str(gq)}
        if aq != wb and _powmod(aq, P - 1, P) != 1:
            return False, f"Fermat check failed for Pocklington base {aq} (composite P)", {}
        q_prod = math.prod(qs_list)
        root_val = _powmod(aq, (P - 1) // q_prod, P)
        rems = _cofactor_tree(qs_list, root_val)
        for q, rem_q in zip(qs_list, rems):
            gq2 = math.gcd(rem_q - 1, P)
            if 1 < gq2 < P:
                return False, f"COMPOSITE_FACTOR_FOUND: factor={gq2} (Pocklington gcd)", {"factor": str(gq2)}
            if gq2 != 1:
                return False, f"Pocklington witness condition gcd(a^((P-1)/{q}) - 1, P) == 1 failed", {}

    gf = math.gcd(F, P)
    if 1 < gf < P:
        return False, f"COMPOSITE_FACTOR_FOUND: factor={gf}", {"factor": str(gf)}

    # Check divisor interval [F + 1, isqrt(P)]
    S = math.isqrt(P)
    alpha = _log2_int(F) / _log2_int(P)

    if S < F + 1:
        if not metadata_ok:
            return False, f"Claimed certificate metadata is not PRIME/true (verdict={cert['verdict']!r})", {}
        return True, f"PRIME ({len(str(P))} digits, alpha={alpha:.6f}, Proth/Pocklington F+1 > sqrt(P))", {
            "digits": len(str(P)),
            "alpha": alpha,
            "slabs": 0,
        }

    # Check BLS Theorem 5 quick composite screen when F^3 > P and gcd(F, R) == 1
    if F ** 3 > P and math.gcd(F, R) == 1:
        c1, c2 = R % F, R // F
        disc = c1 * c1 - 4 * c2
        if disc >= 0:
            s_disc = math.isqrt(disc)
            if s_disc * s_disc == disc and (c1 - s_disc) % 2 == 0:
                k1 = (c1 - s_disc) // 2
                if k1 >= 1:
                    cand = k1 * F + 1
                    if 1 < cand < P and P % cand == 0:
                        return False, f"COMPOSITE_FACTOR_FOUND: factor={cand} (BLS quadratic)", {"factor": str(cand)}

    if "slabs" in lparams:
        raw_slabs = lparams["slabs"]
        slabs_tampered = False
        tamper_reason = ""

        if "P_sha256" in lparams and lparams["P_sha256"] != _sha256_dec(P):
            slabs_tampered = True
            tamper_reason = "P_sha256 binding mismatch in lattice_params"
        elif "F_sha256" in lparams and lparams["F_sha256"] != _sha256_dec(F):
            slabs_tampered = True
            tamper_reason = "F_sha256 binding mismatch in lattice_params"
        elif not isinstance(raw_slabs, list) or len(raw_slabs) == 0:
            slabs_tampered = True
            tamper_reason = "slabs must be a non-empty list covering [F+1, isqrt(P)]"

        if not slabs_tampered:
            try:
                prev_hi = F
                F_inv = pow(F, -1, P)
                max_d_seen = 1
                for j, sl in enumerate(raw_slabs):
                    if not isinstance(sl, dict):
                        raise ValueError(f"slab {j} is not a dict")
                    M_lo = _parse_int_field(sl["M_lo"], f"slabs[{j}].M_lo")
                    M_hi = _parse_int_field(sl["M_hi"], f"slabs[{j}].M_hi")
                    if M_lo != prev_hi + 1 or M_lo > M_hi:
                        raise ValueError(f"slab {j} gap/inversion: expected M_lo={prev_hi + 1}, got [{M_lo}, {M_hi}]")
                    prev_hi = M_hi

                    req_k_lo = max(1, (M_lo - 1 + F - 1) // F)
                    req_k_hi = (M_hi - 1) // F
                    mode = sl.get("mode")

                    if mode == "scan":
                        if req_k_hi - req_k_lo > 5000:
                            raise ValueError(f"scan slab {j} span {req_k_hi - req_k_lo} exceeds 5000")
                        for k in range(req_k_lo, req_k_hi + 1):
                            g = math.gcd(k * F + 1, P)
                            if 1 < g < P:
                                return False, f"COMPOSITE_FACTOR_FOUND: factor={g} (scan slab {j})", {"factor": str(g)}
                    elif mode == "lll":
                        m = sl.get("m")
                        d = sl.get("d")
                        if not _is_strict_int(m) or not _is_strict_int(d) or m < 1 or d <= m or d > 64:
                            raise ValueError(f"invalid (m, d)=({m}, {d}) on slab {j}")
                        max_d_seen = max(max_d_seen, int(d))
                        k_mid = _parse_int_field(sl["k_mid"], f"slabs[{j}].k_mid")
                        X = _parse_int_field(sl["X"], f"slabs[{j}].X")
                        if X < 1:
                            raise ValueError(f"invalid X={X} on slab {j}")
                        if req_k_lo <= req_k_hi:
                            if k_mid - X > req_k_lo or k_mid + X < req_k_hi:
                                raise ValueError(f"box [k_mid-X, k_mid+X] on slab {j} does not cover [k_lo, k_hi]")
                        raw_u = sl.get("u")
                        if not isinstance(raw_u, list) or len(raw_u) != d:
                            raise ValueError(f"slab {j} vector u must have length d={d}")
                        u = [_parse_int_field(ui, f"slabs[{j}].u") for ui in raw_u]
                        if not any(u):
                            raise ValueError(f"slab {j} vector u is identically zero")

                        c_shift = (F_inv + k_mid) % P
                        basis = build_hnf_polys(P, c_shift, int(m), int(d))
                        H = reconstruct_poly_from_u(basis, u)
                        if not any(H):
                            raise ValueError(f"slab {j} reconstructed polynomial H(y) is zero")
                        l1_norm = poly_scaled_l1_norm(H, X)
                        if l1_norm >= M_lo ** int(m):
                            raise ValueError(f"slab {j} fails strict Howgrave-Graham L1 bound: {l1_norm} >= M_lo^{m}")
                        for rt in exact_int_roots_in_box(H, -X, X):
                            k_val = k_mid + rt
                            if k_val >= 1:
                                g = math.gcd(k_val * F + 1, P)
                                if 1 < g < P:
                                    return False, f"COMPOSITE_FACTOR_FOUND: factor={g} (LLL slab {j})", {"factor": str(g)}
                    else:
                        raise ValueError(f"unknown slab mode {mode!r} on slab {j}")

                if prev_hi != S:
                    raise ValueError(f"last slab M_hi={prev_hi} does not reach isqrt(P)={S}")
                if int(cert["lattice_dim"]) < max_d_seen:
                    raise ValueError(f"claimed lattice_dim={cert['lattice_dim']} < slab d_max={max_d_seen}")
            except Exception as exc:
                slabs_tampered = True
                tamper_reason = str(exc)

        if slabs_tampered:
            # If someone forged a certificate by pasting composite P over an existing cert,
            # also run live factor recovery on moderate P so we report the explicit factor!
            if P.bit_length() <= 6000:
                try:
                    _, live_msg, fac, _ = _live_factor_or_certify_divisor_interval(P, F)
                    if fac is not None:
                        return False, f"{live_msg} [slabs also invalid: {tamper_reason}]", {"factor": str(fac)}
                except Exception:
                    pass
            return False, f"Slab certificate verification failed: {tamper_reason}", {}

        if not metadata_ok:
            return False, f"Claimed certificate metadata is not PRIME/true (verdict={cert['verdict']!r})", {}

        return True, f"PRIME ({len(str(P))} digits, alpha={alpha:.6f}, slabs={len(raw_slabs)})", {
            "digits": len(str(P)),
            "alpha": alpha,
            "slabs": len(raw_slabs),
        }

    # Case II: Minimal Contract #4 JSON without precomputed `slabs` -> run live slab-covering qflll!
    try:
        live_ok, live_msg, fac, n_slabs = _live_factor_or_certify_divisor_interval(P, F)
    except Exception as exc:
        return False, f"Live Coppersmith qflll verification failed: {exc}", {}

    if not live_ok:
        details = {"factor": str(fac)} if fac is not None else {}
        return False, live_msg, details
    if not metadata_ok:
        return False, f"Claimed certificate metadata is not PRIME/true (verdict={cert['verdict']!r})", {}

    return True, f"PRIME ({len(str(P))} digits, alpha={alpha:.6f}, live_slabs={n_slabs})", {
        "digits": len(str(P)),
        "alpha": alpha,
        "slabs": n_slabs,
    }


def verify(cert_or_path: dict[str, Any] | str | Path, raise_on_fail: bool = False) -> bool:
    """Boolean wrapper around verify_cert(cert_or_path)."""
    ok, msg, _ = verify_cert(cert_or_path)
    if not ok and raise_on_fail:
        raise AssertionError(msg)
    return ok


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
def _load_record_pf(record_path: str, F_override: str | None, n_override: int | None) -> tuple[int, int, int | None]:
    rec = json.loads(Path(record_path).read_text(encoding="utf-8"))
    if "P" in rec:
        P_val = int(rec["P"])
    elif "N" in rec and "g" in rec:
        P_val = int(rec["N"]) - int(rec["g"])
    else:
        raise ValueError(f"Record {record_path} has neither 'P' nor ('N', 'g')")

    wb = rec.get("witness_base", rec.get("base", rec.get("bls_base")))
    wb_int = int(wb) if wb is not None else None

    if F_override is not None:
        F_val = int(F_override)
    elif n_override is not None:
        F_val = 1 << int(n_override)
    elif "F" in rec:
        F_val = int(rec["F"])
    else:
        v2 = ((P_val - 1) & -(P_val - 1)).bit_length() - 1
        F_val = 1 << v2
    return P_val, F_val, wb_int


def main(argv: list[str] | None = None) -> int:
    args_raw = list(sys.argv[1:] if argv is None else argv)
    if args_raw and args_raw[0] in ("verify", "prove"):
        args_raw[0] = f"--{args_raw[0]}"

    ap = argparse.ArgumentParser(description="Coppersmith--Howgrave-Graham F > P^(1/4+eps) N-1 prover & verifier")
    ap.add_argument("--verify", metavar="CERT_JSON", help="Independently verify a Contract #4 certificate JSON")
    ap.add_argument("--prove", action="store_true", help="Prove primality (or factor composite) and emit Contract #4 JSON")
    ap.add_argument("--P", type=str, default=None, help="Candidate odd integer P")
    ap.add_argument("--F", type=str, default=None, help="Factored divisor F of P - 1 with F > P^(1/4)")
    ap.add_argument("--R", type=str, default=None, help="Optional cofactor R = (P - 1) / F")
    ap.add_argument("--m", type=str, default=None, help="Proth multiplier m for P = m * 2^n + 1")
    ap.add_argument("--n", type=int, default=None, help="2-adic exponent n (P = m * 2^n + 1, or F = 2^n if --P given)")
    ap.add_argument("--from-record", type=str, default=None, help="Load P = N - g from a Proth/BLS record JSON")
    ap.add_argument("--n-override", type=int, default=None, help="Override F = 2^n_override when using --from-record")
    ap.add_argument("--witness-base", "--base", dest="witness_base", type=int, default=None, help="Explicit Euler(-1) witness base")
    ap.add_argument("--k-scan", type=int, default=1000, help="Direct GCD scan bound for small k (<= 5000)")
    ap.add_argument("--out", "-o", "--output", "--json-out", "--cert-out", dest="out", type=str, default=None, help="Output certificate JSON path")
    ap.add_argument("positional", nargs="*", help="Optional positional args")

    try:
        ns = ap.parse_args(args_raw)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    if ns.verify:
        try:
            ok, msg, details = verify_cert(ns.verify)
        except Exception as exc:
            print(f"VERIFICATION FAILED: Unexpected verifier error: {exc}")
            return 1
        if ok:
            print(f"PASS: {msg}")
            return 0
        fac_str = f" [factor={details['factor']}]" if "factor" in details else ""
        print(f"VERIFICATION FAILED: {msg}{fac_str}")
        return 1

    # Prove mode (triggered by --prove or --P / --m / --from-record)
    if not (ns.prove or ns.P or ns.m or ns.from_record or ns.positional):
        ap.print_help(sys.stderr)
        return 2

    try:
        P_val: int
        F_val: int | None = None
        wb_val = ns.witness_base

        if ns.from_record:
            P_val, F_val, rec_wb = _load_record_pf(ns.from_record, ns.F, ns.n_override)
            if wb_val is None:
                wb_val = rec_wb
        elif ns.P is not None:
            P_val = int(ns.P)
            if ns.F is not None:
                F_val = int(ns.F)
            elif ns.n is not None:
                F_val = 1 << int(ns.n)
        elif ns.m is not None and ns.n is not None:
            P_val = (int(ns.m) << int(ns.n)) + 1
            F_val = int(ns.F) if ns.F is not None else (1 << int(ns.n))
        elif len(ns.positional) >= 1:
            P_val = int(ns.positional[0])
            if len(ns.positional) >= 2:
                F_val = int(ns.positional[1])
            elif ns.F is not None:
                F_val = int(ns.F)
            if len(ns.positional) >= 3 and ns.out is None:
                ns.out = ns.positional[2]
        else:
            print("ERROR: --prove requires (--P [--F]), (--m --n), or (--from-record)", file=sys.stderr)
            return 2

        cert = prove(P_val, F_val, witness_base=wb_val, k_scan=ns.k_scan, R=ns.R)
    except Exception as exc:
        print(f"PROVE ERROR: {exc}", file=sys.stderr)
        return 1

    cert_json = json.dumps(cert, indent=2)
    if ns.out and ns.out != "-":
        out_p = Path(ns.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        tmp_p = out_p.with_name(f"{out_p.name}.tmp.{os.getpid()}")
        tmp_p.write_text(cert_json + "\n", encoding="utf-8")
        tmp_p.replace(out_p)
        log_stream = sys.stdout
    else:
        print(cert_json)
        log_stream = sys.stderr

    if cert.get("verdict") == "PRIME":
        ok_self, msg_self, _ = verify_cert(cert)
        if not ok_self:
            print(f"INTERNAL SELF-VERIFY FAILED: {msg_self}", file=sys.stderr)
            return 1
        print(f"PROVED & VERIFIED: {msg_self}", file=log_stream)
        return 0

    fac_note = f" factor={cert['factor']}" if "factor" in cert else ""
    print(f"NOT PRIME: verdict={cert.get('verdict')}{fac_note}", file=log_stream)
    return 1


if __name__ == "__main__":
    sys.exit(main())

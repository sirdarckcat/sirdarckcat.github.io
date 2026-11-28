#!/usr/bin/env python3
"""Standalone verifier for a certified Goldbach-gap record.

Requires ONLY Python 3 standard library (gmpy2 is used to accelerate if
present, but the proof path is identical without it).

Input: a JSON package
{
  "N": "<decimal>",             # the even integer
  "q": <int>,                   # claimed least Goldbach summand  g(N) = q
  "classes": [[r, b], ...],     # prime moduli & residues: N ≡ b (mod r)
  "t": <int>,                   # N = CRT(classes ∪ {N≡0 mod 2}) + t * M
  "ecpp_cert": [...],           # PARI-style ECPP certificate for N - q
  "claims": {...}               # record claims to check (see below)
}

Checks performed (all must pass):
 A. N reconstructs exactly from the congruence system + t; N is even.
 B. Every prime p < q has N - p composite:
    - p = 2: N - 2 is even and > 2;
    - covered p (p ≡ b mod r for a used class): verifies N ≡ b (mod r),
      hence r | N - p with 1 < r < N - p  => proper divisor;
    - residual p: strong-probable-prime test base 2 (and base 3) must FAIL:
      a failure is a one-sided *proof* of compositeness.
 C. q is prime (trial division), and N - q is prime via the ECPP certificate
    (independently re-verified here, chain terminating below 2^64 with
    deterministic Miller-Rabin on the verified base set).
 D. The claimed record inequalities hold exactly (no rounding):
    claims may contain: {"q_exceeds": X}  => q > X
                        {"N_below": "<decimal>"} => N < that integer
                        {"digits_at_most": D} => len(dec(N)) <= D
Exit code 0 iff everything passes.
"""
import hashlib, json, math, re, sys

_INT_STR_RE = re.compile(r"\s*[+-]?[0-9]+\s*", re.ASCII)

def strict_int(v, name="value"):
    """Parse an exact integer from JSON (int or decimal string); reject bool/float/other."""
    if isinstance(v, bool):
        raise ValueError(f"{name}: boolean is not a valid integer")
    if isinstance(v, int):
        return v
    if isinstance(v, str) and _INT_STR_RE.fullmatch(v):
        return int(v)
    raise ValueError(f"{name}: expected integer or decimal string, got {type(v).__name__}")

def _assert_int(v, name="value"):
    try:
        return strict_int(v, name)
    except (TypeError, ValueError) as exc:
        raise AssertionError(str(exc)) from None

# ---------------------------------------------------------------- utilities
def sieve_flags(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(range(i * i, n + 1, i)))
    return s

def sprp_composite(n, a):
    """True iff a proves n composite by the strong probable-prime test.
    (Primes NEVER return True: this is a rigorous compositeness witness.)"""
    assert n >= 2
    if n == 2: return False
    if n % 2 == 0: return True
    if a % n == 0: return False          # test says nothing when a ≡ 0 (mod n)
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1: return False
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1: return False
    return True

def fast_comp_gmpy2(n, gmpy2_mod):
    """gmpy2-accelerated equivalent of sprp_composite(n, 2) or sprp_composite(n, 3)."""
    return (
        n > 2 and (
            n % 2 == 0
            or (n > 3 and n % 3 == 0)
            or not gmpy2_mod.is_strong_prp(n, 2)
            or (n > 3 and not gmpy2_mod.is_strong_prp(n, 3))
        )
    )

# ------------------------------------------------- ECPP certificate checker
class CompositeFactor(Exception): pass

def egcd(a, b):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        qt, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - qt * x1
        y0, y1 = y1, y0 - qt * y1
    return a, x0, y0

def inv_mod(z, n):
    g, x, _ = egcd(z % n, n)
    if g != 1: raise CompositeFactor(g)
    return x % n

def ec_add(P, Qp, a, n):
    if P is None: return Qp
    if Qp is None: return P
    x1, y1 = P; x2, y2 = Qp
    if (x1 - x2) % n == 0:
        if (y1 + y2) % n == 0:
            if (y1 - y2) % n != 0 and math.gcd(y1 - y2, n) != 1:
                raise CompositeFactor(math.gcd(y1 - y2, n))
            return None
        if (y1 - y2) % n != 0:
            raise CompositeFactor(math.gcd(y1 - y2, n))
        lam = (3 * x1 * x1 + a) * inv_mod(2 * y1, n) % n
    else:
        lam = (y2 - y1) * inv_mod(x2 - x1, n) % n
    x3 = (lam * lam - x1 - x2) % n
    return (x3, (lam * (x1 - x3) - y1) % n)

def ec_mul(k, P, a, n):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a, n)
        P = ec_add(P, P, a, n)
        k >>= 1
    return R

def is_prime_u64(n):
    assert 1 < n < 3317044064679887385961981
    for p in (2,3,5,7,11,13,17,19,23,29,31,37,41):
        if n % p == 0: return n == p
    return not any(sprp_composite(n, a) for a in (2,3,5,7,11,13,17,19,23,29,31,37,41))

def ecpp_verify(cert, expect_top):
    expect_top = _assert_int(expect_top, "expect_top")
    assert isinstance(cert, list) and len(cert) > 0, "empty or non-list certificate"
    parsed = []
    for idx, st in enumerate(cert):
        assert isinstance(st, list) and len(st) == 5, f"step {idx}: expected 5-element list"
        pt = st[4]
        assert isinstance(pt, list) and len(pt) == 2, f"step {idx}: expected 2-element point list"
        N = _assert_int(st[0], f"step {idx} N")
        t = _assert_int(st[1], f"step {idx} t")
        s = _assert_int(st[2], f"step {idx} s")
        a = _assert_int(st[3], f"step {idx} a")
        x = _assert_int(pt[0], f"step {idx} x")
        y = _assert_int(pt[1], f"step {idx} y")
        parsed.append((N, t, s, a, (x, y)))
    assert parsed[0][0] == expect_top, "certificate is not for the claimed integer"
    for idx, (N, t, s, a, (x, y)) in enumerate(parsed):
        assert N > 1 and math.gcd(N, 6) == 1, f"step {idx}: gcd(N,6)!=1"
        m = N + 1 - t
        assert s > 0 and m % s == 0, f"step {idx}: s ∤ m"
        assert t * t <= 4 * N, f"step {idx}: Hasse bound violated"
        q = m // s
        D = q * q + 6 * q + 1 - N
        assert q > 1 and D > 0 and D * D > 16 * q * (q + 1) * (q + 1), f"step {idx}: q <= (N^(1/4)+1)^2"
        b = (y * y - x * x * x - a * x) % N
        assert math.gcd((4 * a * a * a + 27 * b * b) % N, N) == 1, f"step {idx}: singular curve"
        try:
            R = ec_mul(s, (x % N, y % N), a, N)
            assert R is not None, f"step {idx}: [s]P = O"
            assert ec_mul(q, R, a, N) is None, f"step {idx}: [q][s]P != O"
        except CompositeFactor as e:
            raise AssertionError(f"step {idx}: nontrivial gcd {e.args[0]} => N composite")
        if idx + 1 < len(parsed):
            assert parsed[idx + 1][0] == q, f"step {idx}: chain broken"
        else:
            assert 1 < q < 3317044064679887385961981 and is_prime_u64(q), f"final step: q={q} not proven prime"
    return True

# ------------------------------------------------------------------- driver
def main(path):
    try:
        import gmpy2
        fast_comp = lambda n: fast_comp_gmpy2(n, gmpy2)
        print("[info] gmpy2 acceleration available")
    except ImportError:
        fast_comp = None
        print("[info] pure stdlib mode")
    with open(path) as fh:
        pkg = json.load(fh)
    assert isinstance(pkg, dict), "package must be a JSON object"
    for key in ("N", "q", "t", "classes", "ecpp_cert"):
        assert key in pkg, f"missing required field {key!r}"
    N = _assert_int(pkg["N"], "N")
    q = _assert_int(pkg["q"], "q")
    t = _assert_int(pkg["t"], "t")
    assert isinstance(pkg["classes"], list), "classes must be a list"
    classes = []
    for idx, item in enumerate(pkg["classes"]):
        assert isinstance(item, list) and len(item) == 2, f"classes[{idx}]: expected [r, b]"
        classes.append((_assert_int(item[0], f"classes[{idx}][0]"),
                        _assert_int(item[1], f"classes[{idx}][1]")))
    claims = pkg.get("claims", {})
    assert isinstance(claims, dict), "claims must be a JSON object"
    with open(path, "rb") as fh:
        print(f"[input] sha256 of package file: {hashlib.sha256(fh.read()).hexdigest()}")

    assert N > 4 and N % 2 == 0, "N must be even and > 4"
    assert q > 1, "q must be > 1"
    assert q < N, "q must be < N"

    # A. reconstruct N by CRT
    seen_r = set()
    M, N0 = 2, 0                                    # start with N ≡ 0 (mod 2)
    for r, b in sorted(classes):
        assert r not in seen_r, "duplicate modulus"
        seen_r.add(r)
        assert 1 < r < N - q, "witness would not be a proper divisor"
        assert 0 <= b < r, f"bad residue {b} mod {r}"
        assert N % r == b, f"N !≡ {b} (mod {r})"
        assert r < 3317044064679887385961981 and is_prime_u64(r), f"modulus {r} not prime"
        g, inv, _ = egcd(M % r, r)
        assert g == 1, "moduli not coprime"
        N0 = N0 + M * ((b - N0) * inv % r)
        M *= r
    N0 %= M
    assert N == N0 + t * M, "N does not reconstruct from congruences + t"
    assert N % 2 == 0, "N not even"
    print(f"[A] N reconstructed: {len(str(N))} digits, t={t}, {len(classes)} congruences OK")

    # B. all primes p < q have composite complement
    for r, b in classes:
        assert N % r == b, f"N !≡ {b} (mod {r})"
        assert 1 < r < N - q, "witness would not be a proper divisor"
    flags = sieve_flags(q)                          # primes < q  (q excluded below)
    covered = bytearray(q)                          # mark covered primes
    for r, b in classes:
        start = b if b > 0 else r
        for x in range(start, q, r):
            covered[x] = 1
    residual = [p for p in range(3, q, 2) if flags[p] and not covered[p]]
    n_primes = sum(1 for p in range(2, q) if flags[p])
    print(f"[B] primes below q: {n_primes}; residual (uncovered): {len(residual)}")
    assert (N - 2) % 2 == 0 and N - 2 > 2           # p = 2
    for i, p in enumerate(residual):
        c = N - p
        if fast_comp is not None:
            assert fast_comp(c), f"N - {p} is a probable prime! g(N) claim false"
        else:
            assert sprp_composite(c, 2) or sprp_composite(c, 3), \
                f"N - {p} passed SPRP(2,3): cannot certify composite"
        if (i + 1) % 500 == 0:
            print(f"    ... {i+1}/{len(residual)} residual complements proven composite", flush=True)
    print(f"[B] all {len(residual)} residual complements composite; "
          f"all covered complements divisible by their class modulus")

    # C. the partition N = q + (N - q)
    assert q > 1 and all(q % d for d in range(2, math.isqrt(q) + 1)), "q not prime"
    ecpp_verify(pkg["ecpp_cert"], N - q)
    print(f"[C] q = {q} prime (trial division); N - q proven prime by ECPP "
          f"({len(pkg['ecpp_cert'])} steps, independently re-verified)")

    # D. record claims
    if "q_exceeds" in claims:
        q_bound = _assert_int(claims["q_exceeds"], "claims.q_exceeds")
        assert q > q_bound, "q does not exceed claimed bound"
        print(f"[D] q = {q} > {q_bound} OK")
    if "N_below" in claims:
        n_bound = _assert_int(claims["N_below"], "claims.N_below")
        assert N < n_bound, "N not below claimed bound"
        print(f"[D] N < N_bound OK ({len(str(N))} vs {len(str(n_bound))} digits)")
    if "digits_at_most" in claims:
        d_bound = _assert_int(claims["digits_at_most"], "claims.digits_at_most")
        assert len(str(N)) <= d_bound, "too many digits"
        print(f"[D] N has {len(str(N))} <= {d_bound} digits OK")
    print(f"[PASS] g(N) = {q} for the {len(str(N))}-digit N in {path}")

if __name__ == "__main__":
    main(sys.argv[1])

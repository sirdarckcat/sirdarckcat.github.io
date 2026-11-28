"""Standalone verifier for Proth/BLS-certified Goldbach deserts.

    python3 verify.py record.json

Python 3 standard library only (gmpy2 is used for the one big modular
exponentiation if it happens to be installed -- same proof path, just
faster).  Nothing is trusted from the search: N is read as a decimal
string and every claim below is re-derived from N, g and the cover.

Claim: g(N) = g, i.e. g is the least prime p such that N - p is prime.

Proof obligations checked here
  (A) for EVERY prime q < g, N - q is composite:
        q lies in a cover class q = a_r (mod r), and N = a_r (mod r),
        so r | N - q, and N - q > r, so r is a proper divisor.
      (The class 0 mod 2 handles q = 2.)  No probabilistic step, no
      residual primes: the cover is complete below g.
  (B) g is prime (sieve) and P = N - g is prime, by the N-1 test:
        P - 1 = 2^v * u,  F = 2^v,  and  b^((P-1)/2) = -1 (mod P).
        Then every prime factor p of P has ord_p(b) divisible by 2^v, so
        p = 1 (mod F).  If F^2 > P, P is prime (Pocklington/Proth).
        If only F^3 > P: a composite P would be (xF+1)(yF+1) with
        xy < F, x+y < F, so writing (P-1)/F = c2*F + c1 (0 <= c1 < F)
        gives c1 = x+y, c2 = xy and c1^2 - 4*c2 = (x-y)^2 a perfect
        square.  So "c1^2 - 4*c2 is not a square" proves P prime
        (Brillhart-Lehmer-Selfridge 1975, Thm 5).
Exit code 0 iff everything holds.
"""
import json
import sys
import time
from math import isqrt

if hasattr(sys, "set_int_max_str_digits"):      # N has > 4300 decimal digits
    sys.set_int_max_str_digits(0)

try:
    import os
    if os.environ.get("NO_GMPY2"):                  # force the pure-stdlib path
        raise ImportError
    import gmpy2
    _powmod = lambda b, e, m: int(gmpy2.powmod(b, e, m))
    _backend = "gmpy2"
except Exception:
    _powmod = pow
    _backend = "python int"


def verify(path, verbose=True):
    say = print if verbose else (lambda *a, **k: None)
    rec = json.load(open(path))
    N, g = int(rec["N"]), int(rec["g"])
    cover = [(int(r), int(a)) for r, a in rec["cover"]]
    base = int(rec["base"])
    assert len(str(N)) == rec["digits"], "digit count mismatch"

    # ---- sieve of Eratosthenes up to g (also certifies the moduli) -------
    comp = bytearray(g + 1)
    comp[0] = comp[1] = 1
    for i in range(2, isqrt(g) + 1):
        if not comp[i]:
            comp[i * i::i] = b"\x01" * len(range(i * i, g + 1, i))
    assert not comp[g], "g is not prime"

    # ---- the cover: prime moduli, N in each class ------------------------
    rmax = 0
    seen = set()
    for r, a in cover:
        assert 2 <= r < g and not comp[r], f"modulus {r} not a prime below g"
        assert r not in seen, f"modulus {r} repeated"
        assert 0 <= a < r, f"residue {a} out of range mod {r}"
        seen.add(r)
        assert N % r == a, f"N is not {a} mod {r}"
        rmax = max(rmax, r)
    assert (2, 0) in cover and N % 2 == 0, "parity class (2, 0) missing or N odd"
    assert N - g > rmax, "divisors would not be proper"
    say(f"[1] N has {rec['digits']} digits and lies in all {len(cover)} classes "
        f"(prime moduli up to {rmax})")

    # ---- (A) every prime q < g is in a class ------------------------------
    hit = bytearray(g + 1)
    for r, a in cover:
        hit[a::r] = b"\x01" * len(range(a, g + 1, r))
    nprimes = 0
    for q in range(2, g):
        if not comp[q]:
            nprimes += 1
            assert hit[q], f"prime {q} < g is in no cover class"
    assert not hit[g], "g itself is covered, so N - g would be composite"
    say(f"[2] all {nprimes} primes q < g = {g} have a proper divisor r | N - q "
        f"(complete cover, no residuals)")

    # ---- (B) P = N - g is prime: N-1 test with F = 2^v --------------------
    P = N - g
    v = ((P - 1) & -(P - 1)).bit_length() - 1
    F = 1 << v
    t0 = time.time()
    assert _powmod(base, (P - 1) >> 1, P) == P - 1, "Euler condition fails"
    dt = time.time() - t0
    if F * F > P:
        how = "Pocklington/Proth: F^2 > P"
    else:
        assert F ** 3 > P, "factored part 2^v is below P^(1/3)"
        qq = (P - 1) >> v
        c1, c2 = qq % F, qq >> v
        D = c1 * c1 - 4 * c2
        assert D < 0 or isqrt(D) ** 2 != D, "c1^2 - 4*c2 is a perfect square"
        how = "BLS: F^3 > P and c1^2 - 4*c2 is not a square"
    say(f"[3] P = N - g is prime: {base}^((P-1)/2) = -1 (mod P), "
        f"F = 2^{v} ({v}/{P.bit_length()} bits), {how}  "
        f"[{dt:.1f}s, {_backend}]")
    say(f"ALL CHECKS PASSED: g(N) = {g} for this {rec['digits']}-digit N")
    return True


if __name__ == "__main__":
    try:
        verify(sys.argv[1])
    except AssertionError as e:
        print("VERIFICATION FAILED:", e)
        sys.exit(1)

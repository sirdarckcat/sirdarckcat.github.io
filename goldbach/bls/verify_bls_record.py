#!/usr/bin/env python3
"""Independent verifier for BLS-certified Goldbach deserts (stdlib only).

Shares no code with bls_search.py and needs neither gmpy2 nor numpy. It
re-derives every claim from the published congruences:

  1. N = the CRT of the cover pairs, the 2-adic pair and the offset i (via a
     product tree), equal to the stored decimal N; N is even.
  2. Every odd prime q < g lies in some class a_r (mod r), and N = a_r
     (mod r) for every pair. Then r | N - q, and r < N - q, so N - q is
     composite. N - 2 is even and > 2.
  3. g is prime and P = N - g is prime by Brillhart-Lehmer-Selfridge with
     F = 2^n: F | P - 1, F^3 > P, a^((P-1)/2) = -1 (mod P), and
     c1^2 - 4*c2 is not a square, where P = c2*F^2 + c1*F + 1.

Hence g(N) = g, unconditionally (no PRP step, no GRH).

    python3 goldbach/bls/verify_bls_record.py goldbach/bls/rec.json
"""
import hashlib
import json
import math
import sys
import time


def small_primes_below(n):
    s = bytearray([1]) * n
    s[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(n - 1) + 1):
        if s[p]:
            s[p * p::p] = bytearray(len(range(p * p, n, p)))
    return [i for i in range(n) if s[i]]


def is_prime_small(m):
    if m < 2:
        return False
    for d in range(2, math.isqrt(m) + 1):
        if m % d == 0:
            return False
    return True


def crt_tree(pairs):
    """Product-tree CRT, a different algorithm from bls_search's loop."""
    nodes = [(a % m, m) for m, a in pairs]
    while len(nodes) > 1:
        nxt = []
        for k in range(0, len(nodes) - 1, 2):
            (x1, m1), (x2, m2) = nodes[k], nodes[k + 1]
            t = ((x2 - x1) * pow(m1, -1, m2)) % m2
            nxt.append((x1 + m1 * t, m1 * m2))
        if len(nodes) % 2:
            nxt.append(nodes[-1])
        nodes = nxt
    return nodes[0]


def main(path):
    t0 = time.time()
    if hasattr(sys, "set_int_max_str_digits"):  # Python >= 3.11 caps str<->int
        sys.set_int_max_str_digits(0)
    rec = json.load(open(path))
    cover = [(int(r), int(a)) for r, a in rec["cover"]]
    g, n, i = int(rec["g"]), int(rec["n"]), int(rec["i"])
    e2, a2 = rec["two_adic"]
    assert e2 == n + 1 and a2 == g + 1 + (1 << n), "2-adic pair mismatch"
    for r, a in cover:
        assert r % 2 == 1 and is_prime_small(r) and 0 <= a < r
    assert len({r for r, _ in cover}) == len(cover), "repeated modulus"

    # 1. reconstruct N
    N0, L = crt_tree([(1 << e2, a2)] + [(r, a) for r, a in cover])
    P0 = (N0 - g) % L
    N = P0 + i * L + g
    assert str(N) == rec["N"], "stored N differs from reconstruction"
    assert N % 2 == 0
    for r, a in cover:
        assert N % r == a, f"N mod {r} != {a}"

    # 2. every odd prime q < g is covered (mark the progressions a_r + k*r)
    covered = bytearray(g)
    for r, a in cover:
        covered[a::r] = b"\x01" * len(range(a, g, r))
    primes = small_primes_below(g)
    unc = [q for q in primes if q > 2 and not covered[q]]
    assert not unc, f"uncovered primes below g: {unc[:10]}"
    assert N - g > max(r for r, _ in cover), "N too small for proper divisors"

    # 3. g prime, g uncovered, P = N - g prime by BLS
    assert is_prime_small(g)
    assert all(g % r != a for r, a in cover), "g itself is covered"
    P = N - g
    F = 1 << n
    R, rem = divmod(P - 1, F)
    assert rem == 0 and R % 2 == 1, "F = 2^n must exactly divide P - 1"
    assert F ** 3 > P >= F ** 2, "need N^(1/3) < F <= N^(1/2)"
    base = int(rec["bls_base"])
    t1 = time.time()
    x = pow(base, (P - 1) // 2, P)
    t_pow = time.time() - t1
    assert x == P - 1, "Pocklington condition fails"
    # x = -1 gives base^(P-1) = 1 and gcd(x - 1, P) = gcd(-2, P) = 1
    assert math.gcd(x - 1, P) == 1 and pow(x, 2, P) == 1
    c2, c1 = divmod(R, F)
    D = c1 * c1 - 4 * c2
    assert D < 0 or math.isqrt(D) ** 2 != D, "BLS square case: composite"

    sha = hashlib.sha256(rec["N"].encode()).hexdigest()
    print(f"PASS  g(N) = {g:,}")
    print(f"  N: {len(rec['N']):,} digits, sha256(decimal) {sha[:16]}...")
    print(f"  {len(primes):,} primes q < g: q=2 by parity, "
          f"{len(primes) - 1:,} odd q by {len(cover):,} cover congruences")
    print(f"  P = N - g ({len(str(P)):,} digits) prime by BLS, F = 2^{n}, "
          f"base {base}; modexp {t_pow:.1f}s (python int)")
    print(f"  total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1])

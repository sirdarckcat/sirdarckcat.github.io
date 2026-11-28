#!/usr/bin/env python3
"""Format-agnostic independent check of a BLS-certified Goldbach desert.

Reads only N, g, the cover and the witness base, so it accepts both this
directory's records (`bls_base`, odd cover) and goldbach/proth records
(`base`, cover including (2, 0)) from branch ccr-2ce9e63a-hn0fuw. It is
stdlib-only and reuses only the small helpers of verify_bls_record.py; it
shares no code with either search.

Checks: N even; N = a_r (mod r) for every cover pair; every odd prime
q < g is in some class; g is prime and not covered; N - g > max r; with
F = the full power of 2 dividing P - 1 and P = N - g, F^3 > P,
base^((P-1)/2) = -1 (mod P), and (if F^2 <= P) the BLS digit test.

    python3 goldbach/bls/xverify.py <record.json>
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_bls_record import is_prime_small, small_primes_below  # noqa


def main(path):
    sys.set_int_max_str_digits(0)
    rec = json.load(open(path))
    N, g = int(rec["N"]), int(rec["g"])
    base = int(rec.get("base", rec.get("bls_base")))
    cover = [(int(r), int(a)) for r, a in rec["cover"] if int(r) != 2]
    assert N % 2 == 0, "N odd"
    assert len({r for r, _ in cover}) == len(cover), "repeated modulus"
    for r, a in cover:
        assert is_prime_small(r) and 0 <= a < r, f"bad pair ({r}, {a})"
        assert N % r == a, f"N mod {r} != {a}"
    covered = bytearray(g)
    for r, a in cover:
        covered[a::r] = b"\x01" * len(range(a, g, r))
    primes = small_primes_below(g)
    unc = [q for q in primes if q > 2 and not covered[q]]
    assert not unc, f"uncovered primes below g: {unc[:10]}"
    assert is_prime_small(g) and all(g % r != a for r, a in cover)
    assert N - g > max(r for r, _ in cover), "divisors would not be proper"
    P = N - g
    k = ((P - 1) & -(P - 1)).bit_length() - 1
    F = 1 << k
    assert F ** 3 > P, "2-part of P - 1 below P^(1/3)"
    t0 = time.time()
    x = pow(base, (P - 1) // 2, P)
    dt = time.time() - t0
    assert x == P - 1, "Euler/Pocklington condition fails"
    if F * F <= P:
        c2, c1 = divmod((P - 1) >> k, F)
        D = c1 * c1 - 4 * c2
        assert D < 0 or math.isqrt(D) ** 2 != D, "BLS square case"
    print(f"PASS g(N) = {g:,}: {len(rec['N']):,} digits, {len(primes):,} "
          f"primes < g covered by {len(cover):,} odd congruences, F = 2^{k}, "
          f"base {base}; modexp {dt:.0f}s (python int)")


if __name__ == "__main__":
    main(sys.argv[1])

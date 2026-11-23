#!/usr/bin/env python3
"""A desert certified by small factors alone.

    python3 complete_cover.py cover.txt [Q]

cover.txt holds one line "BEST r:a r:a ..." or "COVER k r:a ..." (ptcover output): a class a for each modulus r.
The script finds the largest Q such that every odd prime q < Q lies in the class of some modulus (q = a mod r), or
checks the Q given, builds the even N0 below M = 2*prod(r) in all the classes, and verifies directly that for every
odd prime q < Q the number N - q is divisible by some r with N - q > r, for N = N0 + M (the first member that is
certainly large enough) and hence for every N = N0 + t*M, t >= 1.  No primality or compositeness test is used.
Consequence: no prime p < Q has N - p prime (for p = 2, N - 2 is even), i.e. g(N) >= Q whenever N has a
Goldbach partition at all.
"""
import sys

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

line = next(l for l in open(sys.argv[1]) if l.split() and l.split()[0] in ("BEST", "COVER")).split()
cover = [tuple(map(int, t.split(":"))) for t in line[(1 if line[0] == "BEST" else 2):]]
assert all(0 <= a < r for r, a in cover) and len({r for r, _ in cover}) == len(cover)
odd = [q for q in primes_upto(400000) if q > 2]
def covered(q): return any(q % r == a for r, a in cover)
first_bad = next(q for q in odd if not covered(q))
Q = int(sys.argv[2]) if len(sys.argv) > 2 else first_bad          # every odd prime below first_bad is covered
assert Q <= first_bad, f"the odd prime {first_bad} is not covered"
M, N0 = 2, 0
for r, a in cover:
    t = ((a - N0) * pow(M, -1, r)) % r
    N0 += M * t; M *= r
assert N0 % 2 == 0 and all(N0 % r == a for r, a in cover)
N = N0 + M
rows = [q for q in odd if q < Q]
for q in rows:
    r = next(r for r, a in cover if q % r == a)
    assert (N - q) % r == 0 and N - q > r
print(f"{len(cover)} moduli up to {max(r for r, _ in cover)}; M has {len(str(M))} digits")
print(f"every odd prime q < {Q} ({len(rows)} of them, the largest {rows[-1]}) is in the class of some modulus; first uncovered prime: {first_bad}")
print(f"N0 = {N0}")
print(f"N0 has {len(str(N0))} digits; every N = N0 + t*M (t >= 1; t = 0 too if N0 > {Q + max(r for r, _ in cover)}) has N - q divisible by a modulus for all {len(rows)} rows")
print(f"members below 10^200: {max(0, (10**200 - 1 - N0) // M + 1)}")

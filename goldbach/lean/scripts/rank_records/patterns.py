#!/usr/bin/env python3
"""Patterns in the numbers that arrive at ranks 1..K of the least Goldbach summand.

    python3 -I patterns.py ranks.txt > patterns.txt        (ranks.txt from rank_records.py)
"""
import collections
import itertools
import math
import re
import sys

txt = open(sys.argv[1]).read()
arr = {}
for m in re.finditer(r"## rank (\d+): \d+ arrivals.*\n(.*)\n", txt):
    arr[int(m.group(1))] = [tuple(map(int, t.strip("()").split(","))) for t in m.group(2).split()]
K = max(arr)
LOW = 10 ** 5
allv = sorted({(N, g, j) for j in arr for N, g in arr[j]})
big = [(N, g, j) for N, g, j in allv if N > LOW]
print(f"{len(allv)} arrivals at ranks 1..{K}; {len(big)} of them above 10^5 (used below)\n")


def qr(p):
    return {a * a % p for a in range(1, p)}


print("1. Residues of N. Classes: 0, quadratic residues, non-residues (count; share of the non-zero ones)")
for p in (3, 5, 7, 11, 13, 17, 19, 23):
    R = qr(p)
    c0 = sum(1 for N, g, j in big if N % p == 0)
    cr = sum(1 for N, g, j in big if N % p in R)
    cn = len(big) - c0 - cr
    z = (cn - cr) / math.sqrt(cn + cr)
    print(f"   mod {p:2d}: zero {c0:3d}   residues {cr:3d}   non-residues {cn:3d}   ({cn / (cn + cr):.2f}; {z:+.1f} standard deviations from 1/2)"
          f"   expected zero share 1/{p}: {len(big) / p:.0f}")
print("   by rank, N mod 3 = 1 / 2:", " ".join(f"{j}:{sum(1 for N, g, r in big if r == j and N % 3 == 1)}/{sum(1 for N, g, r in big if r == j and N % 3 == 2)}" for j in range(1, K + 1)))

print("\n2. The value and the number: (N + g) mod 3 for N not divisible by 3 (g > 3):",
      collections.Counter((N + g) % 3 for N, g, j in big if N % 3))

print("\n3. Arrivals closer to each other than their g (shared rows):")
same = 0
for (N1, g1, j1), (N2, g2, j2) in itertools.combinations(big, 2):
    if N2 - N1 < max(g1, g2):
        tag = "   same prime N - g" if N1 - g1 == N2 - g2 else ""
        same += N1 - g1 == N2 - g2
        print(f"   ({N1}, {g1}) rank {j1}   ({N2}, {g2}) rank {j2}   distance {N2 - N1}{tag}")
n = len(big)
exp = sum(2 * max(g1, g2) / max(N1, N2) for (N1, g1, _), (N2, g2, _) in itertools.combinations(big, 2))
print(f"   rough expectation if the arrivals were independent (sum over pairs of 2 g / N): {exp:.3f}")

print("\n4. Growth of the record: N, g, g / ln^2 N, g / (ln^2 N ln ln N)")
for N, g in arr[1]:
    if N > LOW:
        L = math.log(N)
        print(f"   {N:>13} {g:>5}  {g / L ** 2:5.2f}  {g / (L ** 2 * math.log(L)):5.2f}")

print("\n5. Smallest odd prime factor of N (arrivals above 10^5):")
def spf(n):
    while n % 2 == 0:
        n //= 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return d
        d += 2
    return n
c = collections.Counter()
for N, g, j in big:
    f = spf(N)
    c["3" if f == 3 else "5" if f == 5 else "7" if f == 7 else "11..97" if f < 100 else ">=101 or N a power of 2 times a prime"] += 1
print("  ", dict(c))

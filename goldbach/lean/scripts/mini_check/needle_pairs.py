#!/usr/bin/env python3
"""What the needles of the miniature have in common (X = 10^9, level Q = 1000).

    gcc -O3 -march=native -fopenmp -o needles needles.c
    ./needles 1000000000 1000 23 200 all | sort -n > needles_all.txt     (N, rows left at 23, at 200)
    python3 -I needle_pairs.py needles_all.txt > needle_pairs.txt

Three things are measured: pairs closer than Q (and how many such pairs a model predicts with and
without the rows that a neighbour inherits), the residues modulo small primes, and the positions.
"""
import collections
import itertools
import math
import sys


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


Q, X, P_PRIME = 1000, 10 ** 9, 0.485          # 0.485: share of primes among 200-rough numbers below X
rows = [p for p in primes_upto(Q) if p > 2]
rowset = set(rows)
small = [p for p in primes_upto(200) if p > 2]
Ns = [int(l.split()[0]) for l in open(sys.argv[1])]
n = len(Ns)
print(f"{n} needles at level {Q} below 10^9 (even N in [1200, 10^9) with N - q composite for all primes q < {Q})")

close = [(b - a, a) for a, b in itertools.combinations(Ns, 2) if b - a < Q]
print(f"\npairs closer than Q: {len(close)}; expected for independent uniform positions: {n * (n - 1) / 2 * 2 * Q / X:.3f}")
for d, a in sorted(close):
    shared = sum(1 for q in rows if q + d in rowset)
    print(f"  N = {a}, N + {d}: {shared} of the {len(rows)} odd rows of N + {d} are rows of N")

with_shared = without = 0.0
for N in Ns:
    for h in range(2, Q, 2):
        k = kall = 0
        for q in rows:
            m = N + h - q
            if all(m % s for s in small):
                kall += 1
                if (q - h) not in rowset:
                    k += 1
        with_shared += (1 - P_PRIME) ** k
        without += (1 - P_PRIME) ** kall
print(f"model, sum over needles N and even 0 < h < Q of the chance that N + h is a needle:")
print(f"  rows inherited from N counted as composite: {with_shared:.2f}; ignoring that: {without:.3f}")

print("\nresidues (needles per class; odd primes below Q per class):")
for r in (3, 5, 7, 11, 13):
    c = collections.Counter(N % r for N in Ns)
    w = collections.Counter(q % r for q in rows if q != r)
    print(f"  mod {r:2d}: {[c[a] for a in range(r)]} ; {[w[a] for a in range(r)]}")

xs = sorted(N / X for N in Ns)
D = max(max(abs((i + 1) / n - x), abs(i / n - x)) for i, x in enumerate(xs))
print(f"\npositions: Kolmogorov-Smirnov distance from uniform {D:.3f} (5% critical value {1.36 / math.sqrt(n):.3f});")
print(f"  needles per quarter of [0, 10^9): {[sum(1 for x in xs if a <= x < a + 0.25) for a in (0, 0.25, 0.5, 0.75)]}")

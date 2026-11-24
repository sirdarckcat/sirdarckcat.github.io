#!/usr/bin/env python3
"""Greedy residue vector: how far do the odd primes up to x reach when each takes its fullest class?

The odd primes r <= x are taken in increasing order; each gets the nonzero class that contains the
most odd primes below y not yet covered (ties: the smallest class).  For each x the largest y that
leaves nothing uncovered is found by bisection; the reach is the first odd prime the final vector
does not cover.  This recomputes, with independent code, the table of the research session
(goldbach/sublinear/greedy_cover.txt on branch ccr-d4a17dd0-7uu03r).

    python3 -I greedy.py 23 53 100 200 463 1000 3000 10000 > greedy.txt
    python3 -I greedy.py --vector 1000        prints N (even, with the residues of the vector) and the reach
"""
import math
import sys

import numpy as np


def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]


def greedy(mods, rows):
    """classes chosen for the moduli, and the rows left uncovered"""
    alive = rows.copy(); vec = []
    for r in mods:
        r = int(r)
        cnt = np.bincount(alive % r, minlength=r)
        cnt[0] = -1
        a = int(np.argmax(cnt))
        vec.append((r, a))
        alive = alive[alive % r != a]
    return vec, alive


def reach(vec, limit):
    """the first odd prime not covered by the vector (searched below limit)"""
    rows = primes_upto(limit); rows = rows[rows > 2]
    for r, a in vec: rows = rows[rows % r != a]
    return int(rows[0]) if len(rows) else None


def best(x):
    mods = primes_upto(x); mods = mods[mods > 2]
    lo, hi = 2 * x, int(3 * x * math.log(x) ** 2) + 100
    allp = primes_upto(hi); allp = allp[allp > 2]
    def left(y): return len(greedy(mods, allp[allp < y])[1])
    assert left(lo) == 0 and left(hi) > 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if left(mid) == 0: lo = mid
        else: hi = mid
    vec, _ = greedy(mods, allp[allp < lo])
    return len(mods), lo, vec


def crt_even(vec):
    N, M = 0, 2
    for r, a in vec:
        t = ((a - N) * pow(M, -1, r)) % r
        N += M * t; M *= r
    return N


if __name__ == "__main__":
    if sys.argv[1] == "--vector":
        x = int(sys.argv[2]); n, y, vec = best(x)
        N = crt_even(vec); N += 2 * math.prod(r for r, _ in vec)         # large enough for every modulus
        print(N); print(reach(vec, 4 * y)); print(",".join(str(r) for r, _ in vec))
    else:
        print("    x  moduli  largest y left empty  first prime not covered  reach/(x ln x)  reach/(x ln^2 x)")
        for x in map(int, sys.argv[1:]):
            n, y, vec = best(x); g = reach(vec, 4 * y)
            print(f"{x:6d} {n:6d} {y:16d} {g:22d} {g / (x * math.log(x)):14.2f} {g / (x * math.log(x) ** 2):16.2f}", flush=True)

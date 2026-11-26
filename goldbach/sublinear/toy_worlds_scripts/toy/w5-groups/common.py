#!/usr/bin/env python3
"""Shared set-up for the World 5 page: the real 200,000 cover, its rows, the first-order tables.

Coordinates: the 89 odd cover primes r (class a_r in the cover) and the next j primes s > 463.
  cover prime r, class c:  dlt_r(c) = (rows left when the class of r alone is changed to c) - n0   (exact for one change; >= 0 iff the cover is 1-optimal)
  later prime s, class c:  -hit_s(c),  hit_s(c) = number of the cover's n0 = 1502 rows q with q = c mod s
Score (separable, "first order"):  S(N) = n0 + sum_r dlt_r(N mod r) - sum_s hit_s(N mod s).
"""
import os, re, math, numpy as np
REPO = "/home/user/sirdarckcat.github.io/goldbach"
F = os.path.join(REPO, "fscan", "cover", "starts", "q200000_m89.txt")
Q = 200000; X = 10 ** 200
cov = [(int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)", open(F).readline())]
def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]
PR = primes_upto(Q - 1); PR = PR[PR > 2]            # odd primes below Q
SMALL = [int(p) for p in primes_upto(3000)]
def later_primes(j): return [s for s in SMALL if s > 463][:j]
def rows_of(classes):
    alive = np.ones(len(PR), dtype=bool)
    for r, a in classes: alive &= (PR % r) != a
    return PR[alive]
R0 = rows_of(cov); n0 = len(R0)
M = 2 * math.prod(r for r, _ in cov)
def crt(classes, start=(0, 2)):
    N, Mm = start
    for (r, c) in classes:
        t = ((c - N) * pow(Mm, -1, r)) % r; N += Mm * t; Mm *= r
    return N
N0 = crt(cov)
def cover_tables():
    """dlt[r] = int array of length r"""
    out = {}
    for idx, (r, a) in enumerate(cov):
        U = rows_of(cov[:idx] + cov[idx + 1:])
        cnt = np.bincount(U % r, minlength=r)
        d = (len(U) - cnt) - n0
        assert d[a] == 0
        out[r] = d.astype(np.int64)
    return out
def later_tables(js):
    return {s: np.bincount(R0 % s, minlength=s).astype(np.int64) for s in js}

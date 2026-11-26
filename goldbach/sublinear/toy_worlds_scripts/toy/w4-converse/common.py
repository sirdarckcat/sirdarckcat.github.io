#!/usr/bin/env python3
"""Shared loader for the w4-converse page: the real 200,000 cover, its rows, its later primes and their tables."""
import sys, math, numpy as np
SUB = "/home/user/sirdarckcat.github.io/goldbach/sublinear"
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000

def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]

def load():
    """returns (cover list [(r, a_r)], rows = odd primes q < Q in no class of the cover)"""
    l = [x for x in open(COVER) if x.startswith(("COVER", "BEST"))][0].split()
    cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
    PR = primes_upto(Q - 1); PR = PR[PR > 2]
    alive = np.ones(len(PR), dtype=bool)
    for r, a in cov: alive &= (PR % r) != a
    return cov, PR[alive]

def table(rows, s):
    return np.bincount(rows % s, minlength=s)

def later_primes(lo=464, hi=5000):
    P = primes_upto(hi); return [int(x) for x in P[P >= lo]]

def window(cov):
    """N0 (least even member), M = 2 prod r, K = members below 10^200"""
    M = 2; N0 = 0
    for r, a in cov:
        # N = N0 + M t = a (mod r)
        t = ((a - N0) * pow(M, -1, r)) % r
        N0 += M * t; M *= r
    K = (10 ** 200 - N0) // M + 1
    return N0, M, K

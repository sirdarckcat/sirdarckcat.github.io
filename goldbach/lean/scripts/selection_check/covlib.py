"""Shared by fold_check.py and selection_check.py: reading a cover line and listing its rows.  Written from the
description of the file only (lines "COVER <rows> r:a ..."), not from the research session's scripts."""
import math
import numpy as np

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

def read_covers(path):
    out = []
    for line in open(path):
        t = line.split()
        if not t or t[0] != "COVER": continue
        out.append((int(t[1]), {int(x.split(":")[0]): int(x.split(":")[1]) for x in t[2:]}))
    return out

def rows_of(classes, Q, odd_primes=None):
    """the odd primes q < Q with q != a (mod r) for every r:a of the cover"""
    q = odd_primes if odd_primes is not None else primes_upto(Q - 1)[1:]
    q = q[q < Q]
    keep = np.ones(len(q), dtype=bool)
    for r, a in classes.items(): keep &= (q % r != a)
    return q[keep]

def base_probability(classes, digits=200):
    """chance that N - q is prime for a row q: N - q is near 10^digits and has no prime factor among 2 and the moduli"""
    x = 2.0
    for r in classes: x *= r / (r - 1.0)
    return x / (digits * math.log(10))

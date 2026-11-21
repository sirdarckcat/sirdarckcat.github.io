#!/usr/bin/env python3
"""Full congruence cover of the odd primes below Q (no residuals).

Increasing-order greedy, as in the paper (slop/goldbach/paper.tex, Table
tab:results): for r = 3, 5, 7, ... pick the class a_r mod r holding the most
still-uncovered primes, until every odd prime q < Q is covered. The parity
congruence (N even) covers q = 2. Every odd prime r <= r_max ends up a modulus.

    python3 goldbach/bls/full_cover.py 1000000 [--out cover.json]
"""
import argparse
import json
import math

import numpy as np


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for p in range(2, math.isqrt(n) + 1):
        if s[p]:
            s[p * p::p] = False
    return np.nonzero(s)[0].astype(np.int64)


def build(Q):
    targets = primes_upto(Q - 1)
    targets = targets[targets > 2]
    remaining = targets
    cover = []
    r_iter = primes_upto(max(1000, Q))[1:]
    for r in r_iter:
        if remaining.size == 0:
            break
        r = int(r)
        counts = np.bincount(remaining % r, minlength=r)
        a = int(counts.argmax())
        cover.append((r, a))
        remaining = remaining[(remaining % r) != a]
    assert remaining.size == 0, "ran out of moduli"
    return cover, int(targets.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("Q", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    cover, ntarget = build(a.Q)
    lnM = sum(math.log(r) for r, _ in cover)
    info = {"Q": a.Q, "odd_targets": ntarget, "congruences": len(cover) + 1,
            "r_max": cover[-1][0], "digits_M": int(lnM / math.log(10)) + 1}
    print(json.dumps(info))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({**info, "cover": cover}, fh)


if __name__ == "__main__":
    main()

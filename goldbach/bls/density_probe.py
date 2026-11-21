#!/usr/bin/env python3
"""Measure the prime rate among sieve survivors of the BLS progression.

The ladder's cost model predicts one prime per ln P / (e^gamma ln S) tests.
This script tests the first K survivors exhaustively (no early stop) and
compares the observed prime count with that prediction (Poisson sigma).

    python3 goldbach/bls/density_probe.py 100000 --tests 3000
"""
import argparse
import math
import os
import sys
from multiprocessing import Pool

import gmpy2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bls_search as bs  # noqa: E402
from full_cover import build  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("Q", type=int)
    ap.add_argument("--tests", type=int, default=2000)
    ap.add_argument("--sieve", type=int, default=100_000_000)
    ap.add_argument("--offsets", type=int, default=100_000)
    a = ap.parse_args()
    cover, _ = build(a.Q)
    g = bs.least_uncovered_prime(a.Q, cover)
    M = gmpy2.mpz(1)
    for r, _ in cover:
        M *= r
    n = (int(M.bit_length()) + (a.offsets + 1).bit_length() + 1) // 2 + 2
    N0, L = bs.crt([(1 << (n + 1), g + 1 + (1 << n))] + cover)
    P0 = (N0 - g) % L
    alive = bs.sieve_offsets(P0, L, a.offsets, cover[-1][0], a.sieve,
                             lambda m: None)
    cand = np.nonzero(alive)[0][: a.tests].tolist()
    args = (P0.digits(16), L.digits(16))
    with Pool(os.cpu_count(), initializer=bs._init, initargs=args) as pool:
        hits = sum(ok for _, _, ok in pool.imap(bs._test, cand, chunksize=4))
    lnP = float(gmpy2.log(P0 + L * cand[-1]))
    rate = math.exp(0.5772156649015329) * math.log(a.sieve) / lnP
    exp = rate * len(cand)
    z = (hits - exp) / math.sqrt(exp)
    print(f"Q={a.Q:,}: P ~{int(lnP / math.log(10)):,} digits, "
          f"{len(cand):,} tests -> {hits} primes; model {exp:.1f} "
          f"(1 per {1 / rate:.0f}); z = {z:+.2f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Time of the block sieve on the campaign3 spec: us per member vs the sieve bound B and the block size K.

    python3 bench_sieve200.py [--rows N] [--B 100000,1000000] [--logK 15,17,19] [--reps 5] [--march ...]
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sieve200 import Sieve200  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=0, help="use the first N residual rows (0: all)")
    ap.add_argument("--B", default="100000,300000,1000000,3000000")
    ap.add_argument("--logK", default="15,17,19")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--march", default=None)
    ap.add_argument("--nocounts", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json")))
    U = spec["residual"][:a.rows] if a.rows else spec["residual"]
    cover = [r for r, _ in spec["cover"]]
    print(f"{len(U)} rows, N0 {int(spec['N0']).bit_length()} bits, M {int(spec['M']).bit_length()} bits")
    print(f"{'B':>9} {'primes':>7} {'logK':>4} {'ms/block':>9} {'us/member':>10} {'ns/(row*member)':>16} {'alive/k':>8}")
    for B in map(int, a.B.split(",")):
        for lk in map(int, a.logK.split(",")):
            sv = Sieve200(int(spec["N0"]), int(spec["M"]), U, B, logK=lk, exclude=cover, march=a.march)
            bits = np.empty((sv.nU, sv.words), dtype=np.uint64)
            sv.block(12345, counts=not a.nocounts, bits=bits)       # warm up
            ts = []
            for r in range(a.reps):
                t = time.perf_counter()
                cnt, _ = sv.block(1000003 * (r + 1), counts=not a.nocounts, bits=bits)
                ts.append(time.perf_counter() - t)
            t = min(ts)
            ak = f"{cnt.mean():8.1f}" if cnt is not None else "       -"
            print(f"{B:9d} {sv.nS:7d} {lk:4d} {1e3 * t:9.2f} {1e6 * t / sv.K:10.3f} {1e9 * t / sv.K / sv.nU:16.4f} {ak}", flush=True)


if __name__ == "__main__":
    main()

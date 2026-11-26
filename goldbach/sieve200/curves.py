#!/usr/bin/env python3
"""Cost of the sieve against its bound B, and what depth buys, on the campaign3 spec (one core).

For each B: sieve time per member for a window of K members; the counts of the window; the probability p_B that a
survivor of the emptiest 8% of members is prime and the number of Fermat tests until a member's first probable prime,
both measured with the production loop (rows in increasing order, stop at the first pass); hit% of testing the emptiest
(1 - skip) of the members, from the model (1 - p_B)^count as in search.py's log.

    python3 curves.py [--B 100000,1000000,10000000] [--logK 19,22] [--members 1500] [--rows N]
"""
import argparse
import json
import math
import os
import random
import sys
import time

import numpy as np
from gmpy2 import mpz, powmod

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sieve200 import Sieve200  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", default="100000,300000,1000000,3000000,10000000,30000000,100000000")
    ap.add_argument("--logK", default="19")
    ap.add_argument("--members", type=int, default=1500, help="members of the emptiest 8%% to test in sequence")
    ap.add_argument("--skip", type=float, default=0.92)
    ap.add_argument("--rows", type=int, default=0)
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json")))
    U = spec["residual"][:a.rows] if a.rows else spec["residual"]
    N0, M = mpz(spec["N0"]), mpz(spec["M"])
    cover = [r for r, _ in spec["cover"]]
    cq = [N0 - q for q in U]
    rng = random.Random(5)
    print(f"{len(U)} rows; members tested in sequence: {a.members} of the emptiest {100 * (1 - a.skip):.0f}%")
    print(f"{'B':>10} {'primes':>8} {'logK':>4} {'ms':>8} {'us/mem':>7} | {'alive':>6} {'sd':>5} {'c@8%':>5} | {'tests/mem':>9} {'p_B':>7} "
          f"{'mertens':>7} | {'hit%':>5}", flush=True)
    for B in map(int, a.B.split(",")):
        for lk in map(int, a.logK.split(",")):
            t = time.perf_counter()
            sv = Sieve200(int(N0), int(M), U, B, logK=lk, exclude=cover)
            tctx = time.perf_counter() - t
            bits = np.empty((sv.nU, sv.words), dtype=np.uint64)
            k0 = 1000003 * 977
            sv.block(k0 + 12345, bits=bits)                       # warm-up: first touch of the memory is slow in a VM
            t = time.perf_counter()
            cnt, _ = sv.block(k0, bits=bits)
            dt = time.perf_counter() - t
            K = sv.K
            c = cnt.astype(np.int64)
            keep = int(math.ceil(K * (1 - a.skip)))
            order = np.argsort(c, kind="stable")[:keep]
            # tests until the first probable prime, for random members of the selected ones
            if a.members == 0:
                print(f"{B:10d} {sv.nS:8d} {lk:4d} {1e3 * dt:8.0f} {1e6 * dt / K:7.3f} | {c.mean():6.1f} {c.std():5.1f} {c[order[-1]]:5d}", flush=True)
                del sv, bits
                continue
            pick = np.array(sorted(rng.sample(range(keep), min(a.members, keep))))
            js = np.ascontiguousarray(order[pick], dtype=np.uint32)
            rows, offs = sv.survivors(bits, js)
            tests = prps = 0
            for i, j in enumerate(js):
                n0 = cq[0] * 0 + (k0 + int(j)) * M
                for r in rows[offs[i]:offs[i + 1]].tolist():
                    n = cq[r] + n0
                    tests += 1
                    if powmod(2, n - 1, n) == 1:
                        prps += 1
                        break
            pB = prps / tests
            w = (1 - pB) ** c.astype(np.float64)
            hit = w[order].sum() / w.sum()
            # Mertens estimate: 1/ln(N) * e^gamma * ln B, times the correction for the cover primes
            lnN = float(spec["N0"].__len__()) * math.log(10) if False else math.log(float(N0) + 0.0)
            mert = math.exp(0.5772156649) * math.log(B) / lnN
            print(f"{B:10d} {sv.nS:8d} {lk:4d} {1e3 * dt:8.0f} {1e6 * dt / K:7.3f} | {c.mean():6.1f} {c.std():5.1f} {c[order[-1]]:5d} | "
                  f"{tests / len(js):9.2f} {pB:7.4f} {mert:7.4f} | {100 * hit:5.1f}   (ctx {tctx:.1f}s)", flush=True)
            del sv, bits


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Microseconds per member of the whole feeder (sieve, counts, selection, survivor lists) on one core.

    python3 bench_feeder.py [--cover spec.json] [--B 1000000] [--logK 19] [--L 15] [--f 0.97,0.99] [--reps 3]
"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sieve200 import Feeder

ap = argparse.ArgumentParser()
ap.add_argument("--cover", default=os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json"))
ap.add_argument("--B", type=int, default=1000000)
ap.add_argument("--logK", type=int, default=19)
ap.add_argument("--L", default="15,19")
ap.add_argument("--f", default="0.97,0.99")
ap.add_argument("--reps", type=int, default=3)
a = ap.parse_args()
spec = json.load(open(a.cover)); spec = spec[0] if isinstance(spec, list) else spec
U = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
cover = [r for r, _ in spec["cover"]]
print(f"{len(U)} rows, B={a.B}, K=2^{a.logK}")
print(f"{'L':>6} {'f':>6} {'ms/window':>10} {'sieve':>7} {'rest':>7} {'us/member':>10} {'selected':>9} {'rows out':>9}")
for lL in map(int, a.L.split(",")):
    for f in map(float, a.f.split(",")):
        fd = Feeder(int(spec["N0"]), int(spec["M"]), U, B=a.B, L=1 << lL, logK=a.logK, f=f, exclude=cover)
        fd.window(2 ** 31 + 12345)
        ts, tss = [], []
        for r in range(a.reps):
            t = time.perf_counter(); blocks = fd.window(2 ** 31 + (r + 2) * fd.sv.K); ts.append(time.perf_counter() - t)
            t = time.perf_counter(); fd.sv.block(2 ** 31 + (r + 2) * fd.sv.K, bits=fd.bits); tss.append(time.perf_counter() - t)
        t, ts_ = min(ts), min(tss)
        print(f"2^{lL:<4d} {f:6.3f} {1e3 * t:10.1f} {1e3 * ts_:7.1f} {1e3 * (t - ts_):7.1f} {1e6 * t / fd.sv.K:10.3f} {sum(len(b.k) for b in blocks):9d} {sum(len(b.rows) for b in blocks):9d}")

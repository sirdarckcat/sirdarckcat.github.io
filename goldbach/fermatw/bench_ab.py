#!/usr/bin/env python3
"""A/B of fmw step variants on a noisy machine: alternate runs in one process, report min and median us/test.
    python3 bench_ab.py L variantA variantB [reps] [count]"""
import random, statistics, sys, time
import numpy as np
import fmw
L, va, vb = int(sys.argv[1]), sys.argv[2], sys.argv[3]
reps = int(sys.argv[4]) if len(sys.argv) > 4 else 12
cnt = int(sys.argv[5]) if len(sys.argv) > 5 else 512
bits = 52 * L - 12
rng = random.Random(7)
ns = [rng.getrandbits(bits) | (1 << (bits - 1)) | 1 for _ in range(cnt)]
libs = {v: fmw.lib(L, v, 1) for v in (va, vb)}
nw = libs[va].fmw_words()
buf = np.concatenate([fmw.words(n, nw) for n in ns])
vd = np.zeros(cnt, dtype=np.uint8)
ts = {va: [], vb: []}
for r in range(reps):
    for v in ((va, vb) if r % 2 == 0 else (vb, va)):
        t = time.perf_counter(); libs[v].fmw_test(cnt, buf.ctypes.data, vd.ctypes.data, None); ts[v].append(1e6 * (time.perf_counter() - t) / cnt)
for v in (va, vb):
    print(f"L={L} {v}: min {min(ts[v]):.1f} median {statistics.median(ts[v]):.1f} us/test")

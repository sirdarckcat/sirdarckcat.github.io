#!/usr/bin/env python3
"""Microseconds per base-2 Fermat test of 661-bit numbers: the IFMA libraries given (interleaved rounds, min and median),
and gmpy2.powmod.   python3 bench_fm13.py libfm13.so [other.so ...] [--rounds 30] [--count 256]"""
import argparse, ctypes, os, random, statistics, time
import numpy as np
import gmpy2
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("libs", nargs="*", default=["libfm13.so"])
ap.add_argument("--rounds", type=int, default=30)
ap.add_argument("--count", type=int, default=256)
ap.add_argument("--nogmp", action="store_true")
a = ap.parse_args()
libs = []
for name in a.libs:
    lib = ctypes.CDLL(os.path.join(HERE, name))
    lib.fm13_test.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    libs.append(lib)
rng = random.Random(1)
cnt = a.count
ns = [rng.getrandbits(661) | (1 << 660) | 1 for _ in range(cnt)]
nw = np.stack([np.frombuffer(n.to_bytes(88, "little"), dtype=np.uint64) for n in ns])
v = np.zeros(cnt, dtype=np.uint8)
ts = [[] for _ in libs]
for r in range(a.rounds):
    for i, lib in enumerate(libs):
        t = time.perf_counter(); lib.fm13_test(cnt, nw.ctypes.data, v.ctypes.data, None); ts[i].append(time.perf_counter() - t)
for name, t in zip(a.libs, ts):
    print(f"{name:<22s} min {1e6 * min(t) / cnt:6.2f}  median {1e6 * statistics.median(t) / cnt:6.2f} us per test")
if not a.nogmp:
    gs = [gmpy2.mpz(n) for n in ns[:100]]
    t = []
    for r in range(5):
        t0 = time.perf_counter()
        for n in gs: gmpy2.powmod(2, n - 1, n)
        t.append(time.perf_counter() - t0)
    print(f"{'gmpy2.powmod':<22s} min {1e6 * min(t) / len(gs):6.2f}  median {1e6 * statistics.median(t) / len(gs):6.2f} us per test")

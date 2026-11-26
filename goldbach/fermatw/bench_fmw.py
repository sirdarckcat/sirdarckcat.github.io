#!/usr/bin/env python3
"""microseconds per base-2 Fermat test: fmw (L limbs, variant, groups) against gmpy2.powmod, numbers of 52 L - 12 bits.
    python3 bench_fmw.py L [variant] [groups] [count]"""
import random
import sys
import time

import numpy as np
import gmpy2
import fmw

L = int(sys.argv[1])
var = sys.argv[2] if len(sys.argv) > 2 else "win"
G = int(sys.argv[3]) if len(sys.argv) > 3 else 1
cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 2048
bits = int(sys.argv[5]) if len(sys.argv) > 5 else 52 * L - 12
rng = random.Random(1)
ns = [rng.getrandbits(bits) | (1 << (bits - 1)) | 1 for _ in range(cnt)]
h = fmw.lib(L, var, G)
nw = h.fmw_words()
buf = np.concatenate([fmw.words(n, nw) for n in ns])
vd = np.zeros(cnt, dtype=np.uint8)
h.fmw_test(64, buf.ctypes.data, vd.ctypes.data, None)
t0 = time.perf_counter()
h.fmw_test(cnt, buf.ctypes.data, vd.ctypes.data, None)
dt = time.perf_counter() - t0
gm = [gmpy2.mpz(n) for n in ns[:200]]
t1 = time.perf_counter()
for n in gm:
    gmpy2.powmod(2, n - 1, n)
dg = (time.perf_counter() - t1) / len(gm)
steps = bits - 6
ifma = 3 * L * L + L + (0 if True else 0)
print(f"L={L} {var} G={G} bits={bits}: fmw {1e6 * dt / cnt:.1f} us/test, gmpy2 {1e6 * dg:.1f} us/test, x{dg / (dt / cnt):.1f}; "
      f"{dt * 2.1e9 / (cnt / 8) / steps:.0f} cycles/step/8 lanes at 2.1 GHz ({(L * (L + 1) + 2 * L * L + L) / (dt * 2.1e9 / (cnt / 8) / steps):.2f} IFMA/cycle)")

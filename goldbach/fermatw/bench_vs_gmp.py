#!/usr/bin/env python3
"""fmw (default variant for L) against gmpy2.powmod, alternating runs in one process (the machine may be busy): min and median.
    python3 bench_vs_gmp.py bits [reps] [count]"""
import random, statistics, sys, time
import numpy as np, gmpy2
import fmw
bits = int(sys.argv[1]); reps = int(sys.argv[2]) if len(sys.argv) > 2 else 5; cnt = int(sys.argv[3]) if len(sys.argv) > 3 else 16
L = fmw.limbs_for(bits); h = fmw.lib(L); nw = h.fmw_words()
rng = random.Random(11)
ns = [rng.getrandbits(bits) | (1 << (bits - 1)) | 1 for _ in range(cnt)]
gm = [gmpy2.mpz(n) for n in ns]
buf = np.concatenate([fmw.words(n, nw) for n in ns]); vd = np.zeros(cnt, dtype=np.uint8)
tf, tg = [], []
for r in range(reps):
    t = time.perf_counter(); h.fmw_test(cnt, buf.ctypes.data, vd.ctypes.data, None); tf.append(1e3 * (time.perf_counter() - t) / cnt)
    t = time.perf_counter()
    for n in gm[:4]: gmpy2.powmod(2, n - 1, n)
    tg.append(1e3 * (time.perf_counter() - t) / 4)
print(f"{bits} bits, L = {L} ({fmw.default_variant(L)}): fmw min {min(tf):.1f} median {statistics.median(tf):.1f} ms; gmpy2 min {min(tg):.1f} "
      f"median {statistics.median(tg):.1f} ms; ratio of medians x{statistics.median(tg) / statistics.median(tf):.1f}")

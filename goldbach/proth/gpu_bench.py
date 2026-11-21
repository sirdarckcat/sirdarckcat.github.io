# Colab GPU throughput benchmark for gpu_screen.py at the 5e6, 1e7 and 16M rung sizes.
import random, sys, time
sys.path.insert(0, "/content")
import importlib, gmpy2, numpy as np, cupy as cp
import gpu_screen as gs
importlib.reload(gs)
rng = random.Random(1)
# (label, n, total P bits, gmp s/test on 1 core of the 4-core box, batch sizes)
cases = [("5e6", 37583, 112745, 91, (256, 512, 1024)),
         ("1e7", 67911, 203735, 335, (256, 512)),
         ("16M", 101600, 304800, 816, (128, 256))]
for label, n, pbits, gmp_s, batches in cases:
    mbits = pbits - n
    for B in batches:
        t0 = time.time()
        ms = [gmpy2.mpz(rng.getrandbits(mbits) | (1 << (mbits - 1))) for _ in range(B)]
        bs = gs.BatchScreen(n, ms, gmpy2)
        prep = time.time() - t0
        x = cp.asarray(gs.to_limbs(bs.x0, bs.L)); f = cp.ones(B)
        for _ in range(20):
            x = bs.mont_sq(x, f)
        cp.cuda.Device().synchronize()
        steps = 200
        t0 = time.time()
        for _ in range(steps):
            x = bs.mont_sq(x, f)
        cp.cuda.Device().synchronize()
        per_step = (time.time() - t0) / steps
        K = bs.K0 + n - 1
        per_test = per_step * K / B
        print(f"{label}: L={bs.L} N={bs.N} B={B}: {per_step*1e3:.2f} ms/step, "
              f"{per_test:.2f} s/test (batch {per_step*K/60:.1f} min), "
              f"x{gmp_s/per_test:.0f} vs one GMP core, prep {prep:.0f}s, "
              f"err {bs.max_rounding_error():.1e}", flush=True)
        del bs, x
        cp.get_default_memory_pool().free_all_blocks()

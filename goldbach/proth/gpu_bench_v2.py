# v1 vs v2 Montgomery squaring speed on the GPU (5e6 and 16M rung sizes).
import random, sys, time
sys.path.insert(0, "/content")
import importlib, gmpy2, cupy as cp
import gpu_screen as gs
importlib.reload(gs)
rng = random.Random(2)
for label, n, pbits, B in (("5e6", 37583, 112745, 512), ("16M", 101600, 304800, 256)):
    ms = [gmpy2.mpz(rng.getrandbits(pbits - n) | (1 << (pbits - n - 1))) for _ in range(B)]
    bs = gs.BatchScreen(n, ms, gmpy2)
    x0 = cp.asarray(gs.to_limbs(bs.x0, bs.L)); f = cp.ones(B)
    res = {}
    for rep in range(2):
        for name, sq in (("v1", bs.mont_sq), ("v2", bs.mont_sq2)):
            x = x0
            for _ in range(10): x = sq(x, f)
            cp.cuda.Device().synchronize(); t0 = time.time()
            for _ in range(150): x = sq(x, f)
            cp.cuda.Device().synchronize()
            res.setdefault(name, []).append((time.time() - t0) / 150 * 1e3)
    v1, v2 = min(res["v1"]), min(res["v2"])
    print(f"{label} B={B}: v1 {v1:.2f} ms/step, v2 {v2:.2f} ms/step -> v2 is {v1/v2:.2f}x (GPU shared with the campaign)", flush=True)
    del bs; cp.get_default_memory_pool().free_all_blocks()

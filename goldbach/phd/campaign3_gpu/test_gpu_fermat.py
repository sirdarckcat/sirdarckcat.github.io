"""Check gpu_fermat.Tester against gmpy2 on campaign3 candidates, then time it.

    python3 test_gpu_fermat.py specs_variants.json [samples] [timing_batch]
"""
import json, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz
sys.set_int_max_str_digits(0)
from gpu_fermat import Tester

specs = json.load(open(sys.argv[1]))
S = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
TB = int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 20
rng = np.random.default_rng(1)
bad = 0
for sp in specs[:2]:
    N0, M = mpz(sp["N0"]), mpz(sp["M"])
    U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
    T = Tester(N0, M, U)
    idx = rng.integers(0, len(U), S).astype(np.int32)
    kv = rng.integers(0, 450_000_000, S).astype(np.uint32)
    kv[:64] = [0, 1, 2, 3] * 16                      # the smallest k too
    kv[64:128] = 450_000_000 - 1 - np.arange(64)     # and the largest
    gpu = cp.asnumpy(T.test(idx, kv))
    t0 = time.time()
    ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0
                    for i, k in zip(idx.tolist(), kv.tolist())], dtype=np.uint8)
    tc = time.time() - t0
    mism = int((gpu != ref).sum()); bad += mism
    print(f"{sp['name']}: {S} candidates, {int(ref.sum())} base-2 PRPs, mismatches {mism}; gmpy2 {tc / S * 1e6:.1f} us/test", flush=True)
# timing on one big batch
idx = cp.asarray(rng.integers(0, len(U), TB).astype(np.int32))
kv = cp.asarray(rng.integers(0, 450_000_000, TB).astype(np.uint32))
T.test(idx[:1024], kv[:1024]); cp.cuda.Device().synchronize()
for threads in (64, 128, 256):
    cp.cuda.Device().synchronize(); t0 = time.time()
    out = T.test(idx, kv, threads=threads); cp.cuda.Device().synchronize()
    dt = time.time() - t0
    print(f"timing: {TB} tests in {dt:.2f} s with {threads} threads/block -> {TB / dt:,.0f} tests/s ({int(out.sum())} PRPs)", flush=True)
print("ALL MATCH" if bad == 0 else f"MISMATCHES: {bad}")

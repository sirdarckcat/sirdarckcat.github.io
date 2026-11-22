"""On a GPU: gpu_fermat31 (22 limbs of 31 bits: 737 IMAD.WIDE a step against fermat28's 876) against gmpy2 on campaign3 candidates, then
its speed against gpu_fermat28's best variants, gpu_fermat3 and gpu_fermat (whichever are importable) on the same inputs.

    python3 test_gpu_fermat31.py specs_variants.json [samples] [timing_batch] [klo]    # k in [klo, 2^32), klo = 2^30 by default

Checks (1) the kernels compile and reports their registers and local memory, (2) mismatches against gmpy2 on random candidates
including the smallest and largest k, (3) tests/s of every variant for 64/128/256 threads a block, with "same" = the flags equal the
first variant's.  Put goldbach/phd/campaign3_gpu (gpu_fermat.py, gpu_fermat3.py) on the path to get the older kernels.
The CPU-side checks are test_step31.py and test_fermat31.py (python3, g++, gmpy2).
"""
import json, os, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz
sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpu_fermat31 as g31
try:
    import gpu_fermat28 as g28
except ImportError:
    g28 = None
try:
    import gpu_fermat as g32
except ImportError:
    g32 = None
try:
    import gpu_fermat3 as g33
except ImportError:
    g33 = None

specs = json.load(open(sys.argv[1]))
S = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
TB = int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 20
KLO = int(sys.argv[4]) if len(sys.argv) > 4 else 1 << 30      # smallest k tested: n must be >= 2^642 (production: k in [2^30, 2^32))
rng = np.random.default_rng(1)
ATTRS = ("num_regs", "local_size_bytes", "shared_size_bytes", "max_threads_per_block")
print("fermat31 attributes:", {a: v for a, v in g31.kernel(21).attributes.items() if a in ATTRS})
print("fermat30 attributes:", {a: v for a, v in g31.kernel(21, step_file="fermat30_step.cuh").attributes.items() if a in ATTRS})
bad = 0
for sp in specs[:2]:
    N0, M = mpz(sp["N0"]), mpz(sp["M"])
    U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
    for step in ("fermat31_step.cuh", "fermat30_step.cuh"):
        T = g31.Tester(N0, M, U, kmin=KLO, kopts=dict(step_file=step))
        idx = rng.integers(0, len(U), S).astype(np.int32)
        kv = rng.integers(KLO, 1 << 32, S, dtype=np.uint64).astype(np.uint32)
        kv[:64] = [KLO, KLO + 1, KLO + 2, KLO + 3] * 16
        kv[64:128] = (1 << 32) - 1 - np.arange(64)
        gpu = cp.asnumpy(T.test(idx, kv))
        ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0
                        for i, k in zip(idx.tolist(), kv.tolist())], dtype=np.uint8)
        mism = int((gpu != ref).sum()); bad += mism
        print(f"{sp['name']} {step}: {S} candidates, {int(ref.sum())} base-2 PRPs, mismatches {mism}, flags 2: {int((gpu == 2).sum())}", flush=True)
idx = cp.asarray(rng.integers(0, len(U), TB).astype(np.int32))
kv = cp.asarray(rng.integers(KLO, 1 << 32, TB, dtype=np.uint64).astype(np.uint32))


def timeit(T, threads):
    T.test(idx[:1024], kv[:1024]); cp.cuda.Device().synchronize()
    best = 1e9
    for _ in range(3):
        cp.cuda.Device().synchronize(); t0 = time.time()
        out = T.test(idx, kv, threads=threads); cp.cuda.Device().synchronize()
        best = min(best, time.time() - t0)
    return best, out


ref_out = None
variants = [("fermat31", g31, dict()), ("fermat31 r72", g31, dict(maxreg=72)), ("fermat31 r96", g31, dict(maxreg=96)),
            ("fermat30", g31, dict(step_file="fermat30_step.cuh"))]
if g28:
    variants += [("fermat28 s1 plain", g28, dict(step_file="fermat28_step_s1.cuh")), ("fermat28 s1 asm", g28, dict(step_file="fermat28_step_s1.cuh", asm_mad=True)),
                 ("fermat28 s2 plain", g28, dict())]
for name, mod, kopts in variants:
    try:
        Tt = mod.Tester(N0, M, U, kopts=kopts, kmin=KLO)
        a = mod.kernel(21, **kopts).attributes
    except Exception as e:                                  # a compile error: report it and go on
        print(f"{name}: FAILED to build: {str(e)[:300]}")
        continue
    for threads in (64, 128, 256):
        d, o = timeit(Tt, threads)
        if ref_out is None:
            ref_out = o.get()
        print(f"{name:18s} regs {a['num_regs']:3d} local {a['local_size_bytes']:4d} B  {threads:3d} thr/blk: {TB / d:12,.0f} tests/s  flags same as first: {bool((o.get() == ref_out).all())}", flush=True)
T32 = g32.Tester(N0, M, U) if g32 else None
T33 = g33.Tester3(N0, M, U) if g33 else None
for label, T_ in (("fermat2 (gpu_fermat.py) ", T32), ("fermat3 (gpu_fermat3.py)", T33)):
    if T_:
        for threads in (64, 128, 256):
            d_, o_ = timeit(T_, threads)
            print(f"{label} {threads:3d} thr/blk: {TB / d_:12,.0f} tests/s   flags same as fermat31: {bool((o_.get() == ref_out).all())}")
print("ALL MATCH" if bad == 0 else f"MISMATCHES: {bad}")

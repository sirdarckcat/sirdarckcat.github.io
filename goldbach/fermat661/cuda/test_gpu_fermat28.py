"""On a GPU: gpu_fermat28 against gmpy2 on campaign3 candidates, then its speed against gpu_fermat's (if importable).

    python3 test_gpu_fermat28.py specs_variants.json [samples] [timing_batch] [klo]    # k in [klo, 2^32), klo = 2^30 by default

Checks first (1) the kernel compiles and reports its registers and local memory, (2) mismatches against gmpy2 on random candidates
including the smallest and largest k, (3) tests/s of gpu_fermat28 and of gpu_fermat on the same inputs for 64/128/256 threads.
Put goldbach/phd/campaign3_gpu (gpu_fermat.py) on the path to get the comparison.
"""
import json, os, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz
sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpu_fermat28 as g28
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
k28 = g28.kernel(21)
print("fermat28 attributes:", {a: v for a, v in k28.attributes.items() if a in ("num_regs", "local_size_bytes", "shared_size_bytes", "max_threads_per_block")})
if g32:
    print("fermat2  attributes:", {a: v for a, v in g32.kernel(21).attributes.items() if a in ("num_regs", "local_size_bytes", "shared_size_bytes", "max_threads_per_block")})
bad = 0
for sp in specs[:2]:
    N0, M = mpz(sp["N0"]), mpz(sp["M"])
    U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
    T = g28.Tester(N0, M, U, kmin=KLO)
    idx = rng.integers(0, len(U), S).astype(np.int32)
    kv = rng.integers(KLO, 1 << 32, S, dtype=np.uint64).astype(np.uint32)
    kv[:64] = [KLO, KLO + 1, KLO + 2, KLO + 3] * 16
    kv[64:128] = (1 << 32) - 1 - np.arange(64)
    gpu = cp.asnumpy(T.test(idx, kv))
    ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0
                    for i, k in zip(idx.tolist(), kv.tolist())], dtype=np.uint8)
    mism = int((gpu != ref).sum()); bad += mism
    print(f"{sp['name']}: {S} candidates, {int(ref.sum())} base-2 PRPs, mismatches {mism}, flags 2: {int((gpu == 2).sum())}", flush=True)
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
VARIANTS = [("s2 plain", dict()), ("s2 asm", dict(asm_mad=True)), ("s1 plain", dict(step_file="fermat28_step_s1.cuh")),
            ("s1 asm", dict(step_file="fermat28_step_s1.cuh", asm_mad=True)), ("s4 plain", dict(step_file="fermat28_step_s4.cuh")),
            ("s4 asm", dict(step_file="fermat28_step_s4.cuh", asm_mad=True)),
            ("s1r plain", dict(step_file="fermat28_step_s1r.cuh")), ("s1r asm", dict(step_file="fermat28_step_s1r.cuh", asm_mad=True)),
            ("s2r plain", dict(step_file="fermat28_step_r.cuh")), ("s2r asm", dict(step_file="fermat28_step_r.cuh", asm_mad=True)),
            # "w" = explicit mul.wide.u32 for the m_i n_j products (no dead IADD3 a product on sm_80 / 89: 1,198 SASS instructions a step instead of 1,798)
            ("s1 plain+w", dict(step_file="fermat28_step_s1w.cuh")), ("s2 plain+w", dict(step_file="fermat28_step_w.cuh")),
            ("s1r plain+w", dict(step_file="fermat28_step_s1rw.cuh")),
            ("s2 plain r128", dict(maxreg=128)), ("s2 asm r128", dict(asm_mad=True, maxreg=128)), ("s2 asm r96", dict(asm_mad=True, maxreg=96))]
T32 = g32.Tester(N0, M, U) if g32 else None
T33 = g33.Tester3(N0, M, U) if g33 else None
ref_out = None
for name, kopts in VARIANTS:
    try:
        T28 = g28.Tester(N0, M, U, kopts=kopts, kmin=KLO)
        a = g28.kernel(21, **kopts).attributes
    except Exception as e:                                  # a compile error: report it and go on
        print(f"{name}: FAILED to build: {str(e)[:300]}")
        continue
    for threads in (64, 128, 256):
        d28, o28 = timeit(T28, threads)
        if ref_out is None:
            ref_out = o28.get()
        line = f"{name:9s} regs {a['num_regs']:3d} local {a['local_size_bytes']:4d} B  {threads:3d} thr/blk: {TB / d28:12,.0f} tests/s  flags same as first: {bool((o28.get() == ref_out).all())}"
        if T32 and threads == 128 and name == VARIANTS[0][0]:
            d32, o32 = timeit(T32, threads)
            line += f"   | fermat2 {TB / d32:12,.0f} tests/s, ratio {d32 / d28:.2f}, flags equal: {bool((o28.get() == o32.get()).all())}"
        print(line, flush=True)
for label, T_ in (("fermat2 (gpu_fermat.py) ", T32), ("fermat3 (gpu_fermat3.py)", T33)):
    if T_:
        for threads in (64, 128, 256):
            d_, o_ = timeit(T_, threads)
            print(f"{label} {threads:3d} thr/blk: {TB / d_:12,.0f} tests/s   flags same as fermat28: {bool((o_.get() == ref_out).all())}")
print("ALL MATCH" if bad == 0 else f"MISMATCHES: {bad}")

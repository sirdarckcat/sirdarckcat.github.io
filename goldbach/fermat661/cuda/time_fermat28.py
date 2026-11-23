"""On a GPU: time Fermat step variants of fermat28 for a fixed number of seconds each, to read the SM clock and power beside them (nvidia-smi sampler in
sieve200/cuda/measure_all.sh) and to get tests/s on the production-range candidates.

    python3 time_fermat28.py specs_variants.json [--variant s1r_asm s1rw ...] [--seconds 20] [--threads 128] [--batch 1048576] [--check]

Variants: s1r_asm (redundant limbs, PTX mad.wide: the RTX PRO 6000s' production kernel), s1rw (redundant limbs, mul.wide for m * n: the A100 / L4), s1_asm, s1w, s1, s2w,
s2r_asm / s4r_asm (the production step with 2 / 4 independent accumulators a column: a test of whether the RTX step is latency bound; CPU-verified like the others),
s1r_asm_r80 / s1r_asm_r72 (the production step capped at 80 / 72 registers: 6 / 7 CTAs an SM for a few spills: a test of whether more warps help).
Prints one line a variant: tests/s (median and best of the timed loops), registers, and with --check the flags against gmpy2 on 2,000 candidates.
"""
import argparse, json, os, sys, time
import numpy as np
import cupy as cp
from gmpy2 import mpz
import gmpy2
sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpu_fermat28 as g28

VARIANTS = {
    "s1r_asm": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True),
    "s1rw": dict(step_file="fermat28_step_s1rw.cuh"),
    "s1_asm": dict(step_file="fermat28_step_s1.cuh", asm_mad=True),
    "s1w": dict(step_file="fermat28_step_s1w.cuh"),
    "s1": dict(step_file="fermat28_step_s1.cuh"),
    "s2w": dict(step_file="fermat28_step_w.cuh"),
    "s2r_asm": dict(step_file="fermat28_step_r.cuh", asm_mad=True),             # 2 accumulators a column: 43 more adds a step than s1r_asm on sm_120 (the cost model: -2.5% if the step is throughput bound, faster if latency bound)
    "s4r_asm": dict(step_file="fermat28_step_s4r.cuh", asm_mad=True),           # 4 accumulators a column: 120 more adds (model -7% / faster if latency bound)
    "s1r_asm_r80": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True, maxreg=80),      # 80 registers: 6 CTAs an SM instead of 5, ~10 spilled words (ptxas on sm_120: 40 B of spill stores, 28 B of loads)
    "s1r_asm_r72": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True, maxreg=72),      # 72 registers: 7 CTAs an SM, ~45 spill instructions (160 B / 188 B)
}

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("--variant", nargs="+", default=["s1r_asm", "s1rw"])
ap.add_argument("--seconds", type=float, default=20.0)
ap.add_argument("--threads", type=int, default=128)
ap.add_argument("--batch", type=int, default=1 << 20)
ap.add_argument("--kmin", type=int, default=1 << 30)
ap.add_argument("--check", action="store_true")
a = ap.parse_args()
specs = json.load(open(a.spec))
sp = specs[0] if isinstance(specs, list) else specs
N0, M = mpz(sp["N0"]), mpz(sp["M"])
U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
rng = np.random.default_rng(1)
idx = cp.asarray(rng.integers(0, len(U), a.batch).astype(np.int32))
kv = cp.asarray(rng.integers(a.kmin, 1 << 32, a.batch, dtype=np.uint64).astype(np.uint32))
print(f"device: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}  batch {a.batch}  threads {a.threads}  {a.seconds:.0f} s a variant", flush=True)
for name in a.variant:
    kopts = VARIANTS[name]
    T = g28.Tester(N0, M, U, kopts=kopts, kmin=a.kmin)
    attrs = g28.kernel(21, **kopts).attributes
    out = T.test(idx[:4096], kv[:4096], threads=a.threads)                       # compile + warm up
    cp.cuda.Device().synchronize()
    if a.check:
        S = 2000
        i2 = rng.integers(0, len(U), S).astype(np.int32)
        k2 = rng.integers(a.kmin, 1 << 32, S, dtype=np.uint64).astype(np.uint32)
        got = cp.asnumpy(T.test(cp.asarray(i2), cp.asarray(k2), threads=a.threads))
        ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0 for i, k in zip(i2.tolist(), k2.tolist())], dtype=np.uint8)
        print(f"  {name}: {int((got != ref).sum())} mismatches against gmpy2 in {S} candidates ({int(ref.sum())} base-2 PRPs)", flush=True)
    rates = []
    t_end = time.time() + a.seconds
    while time.time() < t_end:
        cp.cuda.Device().synchronize()
        t0 = time.time()
        T.test(idx, kv, threads=a.threads)
        cp.cuda.Device().synchronize()
        rates.append(a.batch / (time.time() - t0))
    rates.sort()
    print(f"  {name:8s} regs {attrs['num_regs']:3d} local {attrs['local_size_bytes']:3d} B: median {rates[len(rates) // 2]:12,.0f} tests/s  best {rates[-1]:12,.0f}  ({len(rates)} loops)", flush=True)

#!/usr/bin/env python3
"""89-moduli vectors at the new k range, on the GPU (run from sieve200/cuda of the production tree):
(1) the deep sieve (BatchFeeder: staged and plain large-prime stage, 512-thread tile CTAs) against sieve200's CPU Feeder on a small instance of the
    spec (its first 40 rows, B = 2^22, windows of 2^21) at k0 = k_lo, the first 200-digit k (not a multiple of the window), and at k_lo + 2^21 + 12345;
(2) the production kernel-28 Fermat flags (fermat28_step_s1r.cuh, PTX mad.wide) of 8,192 random (row, k) pairs with k in [k_lo, k_lo + 2^24)
    against gmpy2: flag 1 exactly when 2^(n-1) = 1 mod n.
    python3 check89.py specs.json        (the first spec is used)"""
import json, os, random, sys
import numpy as np
import cupy as cp
HERE = os.path.abspath(os.getcwd())
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
from bench_batch import prime_tables, window_equal
from gbatch import BatchFeeder
from sieve200 import Feeder
sys.path.insert(0, os.environ.get("FERMAT28_DIR", "/content/f28w"))
import gpu_fermat28 as g28
import gmpy2

spec = json.load(open(sys.argv[1]))[0]
for f in ("residual", "cover"):
    if isinstance(spec.get(f), str):
        spec[f] = json.loads(spec[f])
N0, M = int(spec["N0"]), int(spec["M"])
k_lo = -(-(10 ** 199 - N0) // M)
assert N0 + k_lo * M >= 10 ** 199 > N0 + (k_lo - 1) * M
print(f"{spec['name']}: {len(spec['cover'])} moduli, {len(spec['residual'])} rows, M has {len(str(M))} digits, k_lo = {k_lo} (k_lo mod 2^24 = {k_lo % (1 << 24)}), kmax = {spec['kmax']}", flush=True)
ok = True
rows = [int(q) for q in spec["residual"][:40]]
B, ks, tile = 1 << 22, 21, 19
S, INV, N0M = prime_tables(spec, B)
cover = [int(r) for r, _ in spec["cover"]]
for staged in (True, False):
    bf = BatchFeeder(S, INV, rows, N0M, ks_log=ks, tile_log=tile, llog=15, f=0.97, nthreads=256, split=1_000_000, rg=16, staged=staged, rcta=2, stage_cap=8192,
                     gen_threads=256, tile_threads=512)
    cf = Feeder(N0, M, rows, B=B, L=1 << 15, logK=ks, f=0.97, exclude=cover)
    for k0 in (k_lo, k_lo + (1 << ks) + 12345):
        good = window_equal(bf.window(k0), cf.window(k0))
        print(f"  (1) {'staged' if staged else 'plain'} large-prime stage, {len(rows)} rows, B = 2^22, 2^{ks} members, {bf.n_small} small + {bf.n_large} large primes, "
              f"k0 = {k0}: {'identical to the CPU feeder' if good else 'DIFFERENT'}", flush=True)
        ok &= good
U = [int(q) for q in spec["residual"]]
T = g28.Tester(N0, M, U, kopts=dict(step_file="fermat28_step_s1r.cuh", asm_mad=True), kmin=k_lo, kmax=k_lo + (1 << 24))
rng = random.Random(89)
n = 8192
idx = [rng.randrange(len(U)) for _ in range(n)]
kv = [k_lo + rng.randrange(1 << 24) for _ in range(n)]
flags = cp.asnumpy(T.test(np.array(idx, dtype=np.int32), np.array(kv, dtype=np.uint32)))
ref = np.array([1 if pow(2, (N0 - U[i] + k * M) - 1, N0 - U[i] + k * M) == 1 else 0 for i, k in zip(idx, kv)], dtype=np.uint8)
good = np.array_equal(flags, ref)
print(f"  (2) kernel 28 (s1r, asm) on {n} random (row, k), k in [k_lo, k_lo + 2^24): {int(ref.sum())} probable primes; flags {'identical to gmpy2' if good else 'DIFFERENT: ' + str(int((flags != ref).sum())) + ' mismatches'}", flush=True)
ok &= good
print("CHECK89", "OK" if ok else "FAILED")

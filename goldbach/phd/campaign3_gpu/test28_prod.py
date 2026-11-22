"""fermat2, fermat3 and the six fermat28 variants on production-range candidates (k in [2^30, 2^32), n >= 2^662):
flags against gmpy2 on S candidates, flags against each other on TB random ones, and tests/s at 64/128/256 threads."""
import json, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz
sys.set_int_max_str_digits(0)
sys.path.insert(0, "/content/f28"); sys.path.insert(0, "/content/c3g")
import gpu_fermat28 as g28, gpu_fermat as g2, gpu_fermat3 as g3
spec = json.load(open(sys.argv[1]))[0]
S = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
TB = int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 21
U = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
N0, M = mpz(spec["N0"]), mpz(spec["M"])
assert int(N0) - max(U) + (1 << 30) * int(M) >= 1 << 642 and int(N0) + (1 << 32) * int(M) < 1 << 668
cq = cp.asarray(np.stack([g2.to_limbs(int(N0) - int(q), 21) for q in U])); Mv = cp.asarray(g2.to_limbs(int(M), 21))
def run(kern, idx, kv, threads=128):
    T = int(idx.size); out = cp.empty(T, dtype=cp.uint8)
    kern(((T + threads - 1) // threads,), (threads,), (cq, Mv, idx, kv, out, np.int32(T))); return out
rng = np.random.default_rng(5)
idx = rng.integers(0, len(U), S).astype(np.int32)
kv = rng.integers(1 << 30, 1 << 32, S, dtype=np.uint64).astype(np.uint32)
kv[:8] = [1 << 30, (1 << 30) + 1, (1 << 30) + 2, 1 << 31, (1 << 32) - 4, (1 << 32) - 3, (1 << 32) - 2, (1 << 32) - 1]
ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0
                for i, k in zip(idx.tolist(), kv.tolist())], dtype=np.uint8)
print(f"spec {spec['name']} Q={spec['Q']}: {S} candidates k in [2^30, 2^32), {int(ref.sum())} base-2 PRPs", flush=True)
V = [("fermat2", lambda: g2.kernel(21)), ("fermat3", lambda: g3.kernel(21))]
V += [(f"fermat28 {nm}", (lambda ko: (lambda: g28.kernel(21, **ko)))(ko)) for nm, ko in
      [("s2 plain", {}), ("s2 asm", dict(asm_mad=True)), ("s1 plain", dict(step_file="fermat28_step_s1.cuh")),
       ("s1 asm", dict(step_file="fermat28_step_s1.cuh", asm_mad=True)), ("s4 plain", dict(step_file="fermat28_step_s4.cuh")),
       ("s4 asm", dict(step_file="fermat28_step_s4.cuh", asm_mad=True))]]
bi = cp.asarray(rng.integers(0, len(U), TB).astype(np.int32)); bk = cp.asarray(rng.integers(1 << 30, 1 << 32, TB, dtype=np.uint64).astype(np.uint32))
base = None; bad = 0
for name, mk in V:
    try:
        kern = mk(); a = kern.attributes
    except Exception as e:
        print(f"{name}: BUILD FAILED {str(e)[:300]}", flush=True); continue
    out = cp.asnumpy(run(kern, cp.asarray(idx), cp.asarray(kv)))
    m = int((out != ref).sum()); bad += m
    o = run(kern, bi, bk); cp.cuda.Device().synchronize()
    same = "-" if base is None else str(bool((o == base).all()))
    if base is None: base = o
    rates = []
    for th in (64, 128, 256):
        best = 1e9
        for _ in range(3):
            cp.cuda.Device().synchronize(); t0 = time.time(); run(kern, bi, bk, th); cp.cuda.Device().synchronize(); best = min(best, time.time() - t0)
        rates.append(TB / best)
    print(f"{name:17s} regs {a['num_regs']:3d} local {a['local_size_bytes']:4d} B | vs gmpy2 mismatches {m} | flags = fermat2's on {TB}: {same} | "
          f"tests/s 64/128/256: {rates[0]:,.0f} / {rates[1]:,.0f} / {rates[2]:,.0f}", flush=True)
print("ALL MATCH" if bad == 0 else f"MISMATCHES {bad}")

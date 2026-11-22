"""gpu_fermat3 (dedicated squaring, lazy reduction) against gmpy2 and against gpu_fermat's kernel, then both timed.

    python3 test_fermat3.py SPECS.json [SPECS2.json ...] [--samples 40000] [--batch 4194304]

For each spec file: --samples candidates n = N0 - q + k*M (random residual q, k random below 2^32 plus k = 0..3 and
2^32 - 4..2^32 - 1) tested by both kernels and by gmpy2; then --batch random candidates by both kernels (identical
flags required); then each kernel timed on that batch.
"""
import json, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz
sys.set_int_max_str_digits(0)
from gpu_fermat import Tester
from gpu_fermat3 import Tester3

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opt = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
S, TB = opt("--samples", 40000), opt("--batch", 1 << 22)
files = [a for a in args if a.endswith(".json") and not a.lstrip("-").isdigit()]
rng = np.random.default_rng(3)
bad = bad2 = 0
for fn in files:
    specs = json.load(open(fn))
    sp = specs[0]
    U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
    N0, M = mpz(sp["N0"]), mpz(sp["M"])
    nmax = N0 + (2**32 - 1) * M
    T1, T3 = Tester(N0, M, U), Tester3(N0, M, U, n_max=nmax if nmax < 2**665 else None)
    idx = rng.integers(0, len(U), S).astype(np.int32)
    kv = rng.integers(0, 2**32, S, dtype=np.uint64).astype(np.uint32)
    kv[:8] = [0, 1, 2, 3, 2**32 - 4, 2**32 - 3, 2**32 - 2, 2**32 - 1]
    g1, g3 = cp.asnumpy(T1.test(idx, kv)), cp.asnumpy(T3.test(idx, kv))
    ref = np.array([1 if gmpy2.powmod(2, (N0 - U[i] + int(k) * M) - 1, N0 - U[i] + int(k) * M) == 1 else 0
                    for i, k in zip(idx.tolist(), kv.tolist())], dtype=np.uint8)
    m1, m3 = int((g1 != ref).sum()), int((g3 != ref).sum())
    bad += m1 + m3
    print(f"{fn}: {sp['name']} Q={sp['Q']} n < 2^{int(nmax).bit_length()}: {S} candidates, {int(ref.sum())} PRPs; mismatches vs gmpy2: old {m1}, new {m3}", flush=True)
    bi = cp.asarray(rng.integers(0, len(U), TB).astype(np.int32))
    bk = cp.asarray(rng.integers(0, 2**32, TB, dtype=np.uint64).astype(np.uint32))
    T1.test(bi[:4096], bk[:4096]); T3.test(bi[:4096], bk[:4096]); cp.cuda.Device().synchronize()
    tt = {}
    for name, T in (("old", T1), ("new", T3), ("old", T1), ("new", T3)):
        cp.cuda.Device().synchronize(); t0 = time.time()
        o = T.test(bi, bk); cp.cuda.Device().synchronize()
        tt.setdefault(name, []).append(time.time() - t0)
        if name == "old": o1 = o
        else: o3 = o
    d = int((o1 != o3).sum()); bad2 += d
    to, tn = min(tt["old"]), min(tt["new"])
    print(f"   batch {TB}: flags differ old/new: {d} ({int(o1.sum())} PRPs); old {TB/to:,.0f} tests/s, new {TB/tn:,.0f} tests/s, speedup {to/tn:.3f}x", flush=True)
print("ALL MATCH" if bad == 0 and bad2 == 0 else f"MISMATCHES: vs gmpy2 {bad}, old/new {bad2}")

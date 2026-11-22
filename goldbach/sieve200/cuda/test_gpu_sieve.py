"""On a GPU: the sieve/count/select/rows kernels against sieve200's CPU Feeder, with per-phase times.

    python3 test_gpu_sieve.py spec.json [--B 1000000] [--klog 18] [--llog 15] [--f 0.97] [--k0 4293885952]

Needs gcc, numpy, cupy, gmpy2 and goldbach/search.py (init_spec) on the path; compares for 3 windows: the counts (sha256), the
selected members, their rows and the statistics with the CPU feeder (itself identical to numpy's argsort and to search.run_block),
then prints the time of each phase and members per second.
"""
import argparse, hashlib, json, os, sys, time
import numpy as np
import cupy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from gpu_sieve import GpuFeeder
from sieve200 import Feeder
import search

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("--B", type=int, default=1000000)
ap.add_argument("--klog", type=int, default=18)
ap.add_argument("--llog", type=int, default=15)
ap.add_argument("--f", type=float, default=0.97)
ap.add_argument("--k0", type=int, default=4293885952 - 4293885952 % (1 << 18))
ap.add_argument("--nthreads", type=int, default=256)
a = ap.parse_args()
spec = json.load(open(a.spec)); spec = spec[0] if isinstance(spec, list) else spec
for f in ("residual", "cover"):
    if isinstance(spec.get(f), str):
        spec[f] = json.loads(spec[f])
search.init_spec(spec, a.B, 1 << a.llog)
G = search.G
cover = [r for r, _ in spec["cover"]]
gf = GpuFeeder.from_search_G(G, klog=a.klog, llog=a.llog, f=a.f, nthreads=a.nthreads)
cf = Feeder(int(spec["N0"]), int(spec["M"]), spec["residual"], B=a.B, L=1 << a.llog, logK=a.klog, f=a.f, exclude=cover)
ok = True
K, L = gf.K, gf.L
for t in range(3):
    k0 = a.k0 + t * K
    w = gf.window(k0)
    cp.cuda.Device().synchronize()
    cb = cf.window(k0)
    k = cp.asnumpy(w.k); cnt = cp.asnumpy(w.cnt); offs = cp.asnumpy(w.offs); rows = cp.asnumpy(w.rows)
    pos = 0
    good = True
    for b, fb in enumerate(cb):
        n = len(fb.k)
        good &= np.array_equal(k[pos:pos + n], fb.k) and np.array_equal(cnt[pos:pos + n], fb.cnt)
        good &= np.array_equal(rows[offs[pos]:offs[pos + n]], fb.rows)
        good &= int(w.alive_total[b]) == fb.alive_total and abs(w.hm_all[b] - fb.hm_all) <= 1e-9 * fb.hm_all and abs(w.hm_kept[b] - fb.hm_kept) <= 1e-9 * max(fb.hm_kept, 1e-300)
        pos += n
    print(f"window k0={k0}: {len(cb)} blocks, {pos} members selected: {'identical to the CPU feeder' if good else 'DIFFERENT'}", flush=True)
    ok &= good
# per-phase times
ev = [cp.cuda.Event() for _ in range(6)]
import math
nkeep = int(math.ceil(L * (1 - a.f)))
for rep in range(3):
    k0 = a.k0 + rep * K
    cp.cuda.Device().synchronize(); t0 = time.time()
    w = gf.window(k0); cp.cuda.Device().synchronize(); tw = time.time() - t0
t0 = time.time()
for rep in range(5):
    w = gf.window(a.k0 + rep * K)
cp.cuda.Device().synchronize(); tw = (time.time() - t0) / 5
print(f"window of {K} members: {1e3 * tw:.2f} ms = {1e9 * tw / K:.2f} ns a member = {K / tw / 1e6:.1f} M members/s ({gf.nU} rows, {gf.sh['nS']} primes, f={a.f})")
# the kernels alone
sh = gf.sh
KM = (cp.uint64(a.k0) % sh["S64"].astype(cp.uint64)).astype(cp.uint32)
def tk(fn, n=5):
    fn(); cp.cuda.Device().synchronize(); t0 = time.time()
    for _ in range(n): fn()
    cp.cuda.Device().synchronize(); return (time.time() - t0) / n
tsv = tk(lambda: gf.k["s200g_sieve"]((gf.nU,), (gf.nthreads,), (gf.U, sh["S"], sh["INV"], sh["MU"], gf.N0M, KM, np.int32(sh["nS"]), gf.bits), shared_mem=4 * (K // 32)))
tco = tk(lambda: gf.k["s200g_count"](((K // 32 + gf.nthreads - 1) // gf.nthreads,), (gf.nthreads,), (gf.bits, np.int32(gf.nU), gf.counts)))
print(f"  sieve kernel {1e3 * tsv:.2f} ms ({1e9 * tsv / K:.2f} ns a member), count kernel {1e3 * tco:.3f} ms, rest (select, rows, glue) {1e3 * (tw - tsv - tco):.2f} ms")
print("ALL IDENTICAL" if ok else "MISMATCH")

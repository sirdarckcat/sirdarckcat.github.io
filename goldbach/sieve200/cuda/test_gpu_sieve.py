"""On a GPU: the sieve/count/select/rows kernels against sieve200's CPU Feeder, with per-phase times.

    python3 test_gpu_sieve.py spec.json [--B 1000000] [--klog 19] [--llog 15] [--f 0.97] [--k0 4293885952] [--sieve-threads 1024] [--no-sweep]

First the default GpuFeeder (Shoup setup, --sieve-threads for the sieve kernel, --nthreads for the others) against the CPU feeder on 3 windows; then, unless --no-sweep,
a sweep of the options (original 64-bit kernel / Shoup kernel, sieve CTA size 256 / 512 / 1024, unroll 1 / 3) with the per-phase times of window(timings=True), each
checked to give the same counts and selected members as the first configuration.

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
ap.add_argument("--klog", type=int, default=19)
ap.add_argument("--llog", type=int, default=15)
ap.add_argument("--f", type=float, default=0.97)
ap.add_argument("--k0", type=int, default=4293885952 - 4293885952 % (1 << 18))
ap.add_argument("--nthreads", type=int, default=256)
ap.add_argument("--sieve-threads", type=int, default=None, help="CTA size of the sieve kernel (default: --nthreads)")
ap.add_argument("--no-sweep", action="store_true")
a = ap.parse_args()
spec = json.load(open(a.spec)); spec = spec[0] if isinstance(spec, list) else spec
for f in ("residual", "cover"):
    if isinstance(spec.get(f), str):
        spec[f] = json.loads(spec[f])
search.init_spec(spec, a.B, 1 << a.llog)
G = search.G
cover = [r for r, _ in spec["cover"]]
gf = GpuFeeder.from_search_G(G, klog=a.klog, llog=a.llog, f=a.f, nthreads=a.nthreads, sieve_threads=a.sieve_threads)
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
# the sweep: original 64-bit kernel against the Shoup kernel, sieve CTA sizes, per-phase times (window(timings=True)); same output required
if not a.no_sweep:
    import hashlib
    def digest(w):
        h = hashlib.sha256()
        for arr in (w.k, w.cnt, w.offs, w.rows):
            h.update(cp.asnumpy(arr).tobytes())
        return h.hexdigest()[:12]
    cfgs = [dict(shoup=False, sieve_threads=256), dict(shoup=False, sieve_threads=1024), dict(shoup=True, sieve_threads=256), dict(shoup=True, sieve_threads=512),
            dict(shoup=True, sieve_threads=1024), dict(shoup=True, sieve_threads=1024, unroll=3), dict(shoup=True, sieve_threads=512, unroll=3)]
    print(f"sweep: {gf.nU} rows, {gf.sh['nS']} primes, K = 2^{a.klog}, f = {a.f}; ms a window (mean of 5), the GPU phases from events; ns/member")
    print(f"  {'config':44s} {'wall':>7s} {'ns/m':>6s} | {'prep':>6s} {'sieve':>7s} {'count':>6s} {'select':>7s} {'final':>6s} {'wait1':>6s} {'rows':>6s} {'wait2':>6s} {'host':>6s}  output")
    ref = None
    for cfg in cfgs:
        try:
            g = GpuFeeder.from_search_G(G, klog=a.klog, llog=a.llog, f=a.f, nthreads=a.nthreads, **cfg)
            w = g.window(a.k0); cp.cuda.Device().synchronize()            # compile + warm up
        except Exception as e:
            print(f"  {str(cfg):44s} FAILED: {str(e)[:150]}")
            continue
        d = digest(w)
        ref = ref or d
        acc = {}
        for rep in range(5):
            w = g.window(a.k0 + (rep + 1) * K, timings=True)
            for kk, v in w.timings.items():
                acc[kk] = acc.get(kk, 0.0) + v / 5
        print(f"  {str(cfg):44s} {acc['wall']:7.2f} {1e6 * acc['wall'] / K:6.2f} | {acc['prep']:6.3f} {acc['sieve']:7.3f} {acc['count']:6.3f} {acc['select']:7.3f} {acc['finalize']:6.3f} "
              f"{acc['wait1']:6.3f} {acc['rows']:6.3f} {acc['wait2']:6.3f} {acc['host']:6.3f}  {'same' if d == ref else 'DIFFERENT'}", flush=True)
        ok &= d == ref
print("ALL IDENTICAL" if ok else "MISMATCH")

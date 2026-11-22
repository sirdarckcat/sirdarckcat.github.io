"""Where search_gpu2.py's time goes, and what selective testing (--skip-frac) would pay on the GPU.

Per block (k0 = K0 + i*L): GPU sieve kernel, matrix prep (bool, transpose, counts), then the test
loop for each skip fraction f in FS on the emptiest (1-f) of the block, as search_gpu2.py does it;
also the GPU tests actually computed (wasted after a member's first PRP) and the launch count, and
the loop with D capped. Prints a summary table. Results are not logged anywhere else.
"""
import json, math, sys, time
import numpy as np
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 8
sys.argv = ["search_gpu2.py", "/content/c3g/my_specs.json", "--goldbach", "/content/c3g"]
sys.path.insert(0, "/content/c3g")
import search                       # noqa: E402
import cupy as cp                   # noqa: E402
import cupyx                        # noqa: E402
import search_gpu2                  # noqa: E402
from gpu_fermat import Tester       # noqa: E402
from gmpy2 import mpz               # noqa: E402

K0 = 300_000_000 // 32768 * 32768
FS = [0.0, 0.5, 0.75, 0.9, 0.95, 0.97, 0.98, 0.99]
L, TARGET, PEST = 32768, 262144, 0.055
sync = cp.cuda.Device().synchronize
spec = json.load(open("/content/c3g/my_specs.json"))[3]
for f in ("residual", "cover"):
    if isinstance(spec.get(f), str):
        spec[f] = json.loads(spec[f])
t = time.time(); gs = search_gpu2.GpuSieve(spec, cp); sync(); t_gs = time.time() - t
t = time.time(); tester = Tester(mpz(spec["N0"]), mpz(spec["M"]), spec["residual"]); sync(); t_te = time.time() - t
print(f"spec {spec['name']}: GpuSieve init {t_gs:.2f}s (search.init_spec + A), Tester init {t_te:.2f}s", flush=True)


def test_loop(aliveT, counts, order, dcap=None):
    sub = aliveT[order]
    cnt = counts[order]
    rows, cols = cp.nonzero(sub)
    indptr = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
    cols = cols.astype(cp.int32)
    act = cp.nonzero(cnt > 0)[0]
    pos = cp.zeros(order.size, cp.int64)
    tests = prps = gtests = steps = 0
    nsucc = int((cnt == 0).sum())
    while act.size:
        rem = cnt[act] - pos[act]
        D = int(max(1, min(int(rem.max()), TARGET // int(act.size))))
        if dcap:
            D = min(D, dcap)
        take = cp.minimum(rem, D)
        csum = cp.cumsum(take)
        total = int(csum[-1])
        m_of = cp.searchsorted(csum, cp.arange(total), side="right")
        off = cp.arange(total) - (csum - take)[m_of]
        ip = (indptr[act] + pos[act])[m_of] + off
        flags = tester.test(cols[ip], (k0 + order[act])[m_of].astype(cp.uint32))
        big = D + 1
        first = cp.full(int(act.size), big, dtype=cp.int32)
        cupyx.scatter_min(first, m_of, cp.where(flags.astype(cp.bool_), off, big).astype(cp.int32))
        hit = first < big
        tests += int(cp.where(hit, first + 1, take).sum())
        prps += int(hit.sum())
        gtests += total
        steps += 1
        pos[act] += take
        done = (~hit) & (pos[act] == cnt[act])
        nsucc += int(done.sum())
        act = act[(~hit) & (~done)]
    return tests, prps, gtests, steps, nsucc


acc = {"sieve": 0.0, "prep": 0.0}
R = {f: dict(t=0.0, share=0.0, tests=0, prps=0, gtests=0, steps=0) for f in FS}
RC = {}
for i in range(NB):
    k0 = K0 + i * L
    sync(); t = time.time()
    a8 = gs.block(k0, L)
    sync(); acc["sieve"] += time.time() - t; t = time.time()
    aliveT = cp.ascontiguousarray(a8.astype(cp.bool_).T)
    counts = aliveT.sum(axis=1).astype(cp.int64)
    w = (1.0 - PEST) ** counts.astype(cp.float64)
    wsum = float(w.sum())
    sync(); acc["prep"] += time.time() - t
    for f in FS:
        sync(); t = time.time()
        if f > 0:
            keep = int(math.ceil(L * (1.0 - f)))
            order = cp.lexsort(cp.stack([cp.arange(L), counts]))[:keep]
            share = float(w[order].sum()) / wsum
        else:
            order = cp.arange(L); share = 1.0
        te, pp, gt, st, ns = test_loop(aliveT, counts, order)
        sync(); dt = time.time() - t
        r = R[f]; r["t"] += dt; r["share"] += share / NB; r["tests"] += te; r["prps"] += pp; r["gtests"] += gt; r["steps"] += st
    for f, dcap in ((0.0, 8), (0.0, 4), (0.97, 8), (0.97, 4)):
        sync(); t = time.time()
        order = cp.arange(L) if f == 0 else cp.lexsort(cp.stack([cp.arange(L), counts]))[:int(math.ceil(L * (1.0 - f)))]
        te, pp, gt, st, ns = test_loop(aliveT, counts, order, dcap)
        sync(); dt = time.time() - t
        r = RC.setdefault((f, dcap), dict(t=0.0, tests=0, gtests=0, steps=0))
        r["t"] += dt; r["tests"] += te; r["gtests"] += gt; r["steps"] += st
    print(f"block {i} done", flush=True)

ts, tp = acc["sieve"] / NB, acc["prep"] / NB
print(f"per block: sieve kernel {1e3*ts:.1f} ms, prep (bool, transpose, counts, weights) {1e3*tp:.1f} ms")
print(f"{'f':>5} {'test ms/blk':>11} {'share':>6} {'tests/blk':>10} {'gpu tests/blk':>13} {'waste%':>6} {'launches':>8} {'k/s':>9} {'eff k/s':>9} {'x vs f=0':>8}")
base = None
for f in FS:
    r = R[f]
    tt = r["t"] / NB
    blk = ts + tp + tt
    ks = L / blk
    eff = ks * r["share"]
    base = base or eff
    print(f"{f:5.2f} {1e3*tt:11.1f} {r['share']:6.3f} {r['tests']/NB:10.0f} {r['gtests']/NB:13.0f} {100*(1-r['tests']/max(r['gtests'],1)):6.1f} {r['steps']/NB:8.1f} {ks:9.0f} {eff:9.0f} {eff/base:8.2f}")
for (f, dcap), r in RC.items():
    print(f"D cap {dcap} at f={f}: test {1e3*r['t']/NB:.1f} ms/blk, tests {r['tests']/NB:.0f}, gpu tests {r['gtests']/NB:.0f}, launches {r['steps']/NB:.1f}")
print(f"counted test rate at f=0: {R[0.0]['tests']/R[0.0]['t']:.3e}/s, computed {R[0.0]['gtests']/R[0.0]['t']:.3e}/s")

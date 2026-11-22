#!/usr/bin/env python3
"""gpu_sieve.py (the cupy orchestration of the GPU sieve) run on the CPU: cupy is replaced by numpy plus a RawModule whose kernels are
the pthread emulation of gsieve_kernels.cuh.  Checks the Python glue (shapes, dtypes, offsets, statistics) against sieve200's Feeder.

    python3 test_gpu_sieve_cpu.py [--rows 60]
"""
import argparse, ctypes, json, math, os, re, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gsieve


class _Fn:
    def __init__(self, lib, name):
        self.lib, self.name = lib, name

    def __call__(self, grid, block, args, shared_mem=0):
        P = lambda a: a.ctypes.data
        L = self.lib
        if self.name == "s200g_sieve":
            U, S, INV, MU, N0M, KM, nS, bits = args
            L.cpu_sieve(int(grid[0]), P(U), P(S), P(INV), P(MU), P(N0M), P(KM), int(nS), P(bits))
        elif self.name == "s200g_count":
            bits, nU, counts = args
            L.cpu_count(P(bits), int(nU), P(counts))
        elif self.name == "s200g_select":
            counts, maxc, nkeep, p, keys, stats = args
            L.cpu_select(P(counts), int(maxc), int(nkeep), float(p), P(keys), P(stats))
        elif self.name == "s200g_rows":
            bits, nU, member, offs, nsel, rows = args
            L.cpu_rows(P(bits), int(nU), P(member), P(offs), int(nsel), P(rows))
        elif self.name == "s200g_n0m":
            limbs, nl, S, MU, nS, out = args
            L.cpu_n0m(P(limbs), int(nl), P(S), P(MU), int(nS), P(out))
        else:
            raise KeyError(self.name)


class _RawModule:
    def __init__(self, code=None):
        klog, llog, nth = (int(re.search(rf"#define {n} (\d+)", code).group(1)) for n in ("KLOG", "LLOG", "NTHREADS"))
        self.lib = test_gsieve.build(klog, llog, nth, 8192)

    def get_function(self, name):
        return _Fn(self.lib, name)


def install_fake_cupy():
    cp = types.ModuleType("cupy")
    cp.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
    cp.asnumpy = np.asarray
    cp.RawModule = _RawModule
    class _Dev:
        def synchronize(self): pass
    cp.cuda = types.SimpleNamespace(Device=lambda: _Dev())
    sys.modules["cupy"] = cp
    return cp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=60)
    a = ap.parse_args()
    install_fake_cupy()
    import gpu_sieve
    import search
    from sieve200 import Feeder
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec["residual"] = spec["residual"][:a.rows]
    cover = [r for r, _ in spec["cover"]]
    ok = True
    for B, klog, llog, f in ((20011, 13, 11, 0.9), (100003, 13, 12, 0.5), (5003, 12, 11, 0.0)):
        search.G.clear(); search._SIEVE_CACHE.clear()
        search.init_spec(spec, B, 1 << llog)
        gf = gpu_sieve.GpuFeeder.from_search_G(search.G, klog=klog, llog=llog, f=f, nthreads=64)
        cf = Feeder(int(spec["N0"]), int(spec["M"]), spec["residual"], B=B, L=1 << llog, logK=klog, f=f, exclude=cover)
        for k0 in (4096 * 5, 2 ** 31 + 8192, 4293885952 - 4293885952 % 8192):
            w = gf.window(k0)
            cb = cf.window(k0)
            pos, good = 0, True
            for b, fb in enumerate(cb):
                n = len(fb.k)
                good &= np.array_equal(w.k[pos:pos + n], fb.k) and np.array_equal(w.cnt[pos:pos + n], fb.cnt)
                good &= np.array_equal(w.rows[w.offs[pos]:w.offs[pos + n]], fb.rows) and np.all(w.block[pos:pos + n] == b)
                good &= int(w.alive_total[b]) == fb.alive_total and abs(w.hm_all[b] - fb.hm_all) <= 1e-9 * fb.hm_all
                good &= abs(w.hm_kept[b] - fb.hm_kept) <= 1e-9 * max(fb.hm_kept, 1e-300)
                pos += n
            good &= pos == len(w.k) and w.offs[-1] == len(w.rows)
            print(f"  B={B} K=2^{klog} L=2^{llog} f={f} k0={k0}: {len(cb)} blocks, {pos} members: {'identical to the CPU feeder' if good else 'DIFFERENT'}", flush=True)
            ok &= good
    # another variant of the same M: GpuFeeder.with_variant shares the prime tables
    N0b = int(spec["N0"]) + 987654321 * int(spec["M"]) // 7 + 12345
    n0m_b = np.array([N0b % int(s) for s in search.G["S"]], dtype=np.int64)
    gf2 = gf.with_variant(n0m_b, search.G["U"])
    cf2 = Feeder(N0b, int(spec["M"]), spec["residual"], B=5003, L=1 << 11, logK=12, f=0.0, exclude=cover)
    w, cb = gf2.window(8192), cf2.window(8192)
    pos, good = 0, True
    for b, fb in enumerate(cb):
        n = len(fb.k)
        good &= np.array_equal(w.k[pos:pos + n], fb.k) and np.array_equal(w.rows[w.offs[pos]:w.offs[pos + n]], fb.rows) and int(w.alive_total[b]) == fb.alive_total
        pos += n
    print(f"  with_variant (another N0, same M): {'identical to the CPU feeder' if good else 'DIFFERENT'}")
    ok &= good
    gf3 = gf.with_N0(N0b, search.G["U"])                         # N0 mod s computed by the s200g_n0m kernel
    w3 = gf3.window(8192)
    pos, good = 0, True
    for b, fb in enumerate(cf2.window(8192)):
        n = len(fb.k)
        good &= np.array_equal(w3.k[pos:pos + n], fb.k) and np.array_equal(w3.rows[w3.offs[pos]:w3.offs[pos + n]], fb.rows) and int(w3.alive_total[b]) == fb.alive_total
        pos += n
    good &= np.array_equal(gf3.N0M, n0m_b.astype(np.uint32))
    print(f"  with_N0 (N0 mod s on the GPU kernel): {'identical to the CPU feeder' if good else 'DIFFERENT'}")
    ok &= good
    to_limbs = lambda x: np.frombuffer(int(x).to_bytes(84, "little"), dtype=np.uint32)
    for N0x in (int(spec["N0"]), N0b, (1 << 640) + 5, 70000):
        Ux = [q for q in spec["residual"] if q < N0x]
        good = np.array_equal(gpu_sieve.cq_rows(N0x, Ux), np.stack([to_limbs(N0x - q) for q in Ux])) if Ux else True
        ok &= good
    print(f"  cq_rows equal to to_limbs(N0 - q) row by row: {ok}")
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

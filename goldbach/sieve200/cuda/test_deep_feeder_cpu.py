#!/usr/bin/env python3
"""deep_feeder.py on the CPU (cupy replaced by numpy + the pthread emulation of the kernels): ONE BatchFeeder retargeted over several variants of a campaign (different N0, different
numbers of rows, in any order) must give, for every window, exactly what sieve200's CPU Feeder gives for that variant (counts, selected members, their rows, the statistics);
the numpy prime tables must be the primes search.init_spec makes; deep_feeder_for must keep one DeepSieve per M.

    python3 test_deep_feeder_cpu.py
"""
import json, os, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB


def same(w, cb):
    pos, good = 0, True
    for b, fb in enumerate(cb):
        n = len(fb.k)
        good &= np.array_equal(w.k[pos:pos + n], fb.k) and np.array_equal(w.cnt[pos:pos + n], fb.cnt)
        good &= np.array_equal(w.rows[w.offs[pos]:w.offs[pos + n]], fb.rows) and np.all(w.block[pos:pos + n] == b)
        good &= int(w.alive_total[b]) == fb.alive_total and abs(w.hm_all[b] - fb.hm_all) <= 1e-9 * fb.hm_all
        good &= abs(w.hm_kept[b] - fb.hm_kept) <= 1e-9 * max(fb.hm_kept, 1e-300)
        pos += n
    return bool(good) and pos == len(w.k)


def main():
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    import deep_feeder as DF
    import search
    from sieve200 import Feeder
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    cover = [int(r) for r, _ in spec["cover"]]
    M, N0 = int(spec["M"]), int(spec["N0"])
    U = [int(q) for q in spec["residual"]]
    ok = True

    # 1. the numpy prime tables are search.init_spec's S and M^-1 mod s
    for B in (1000, 20011):
        search.G.clear(); search._SIEVE_CACHE.clear()
        search.init_spec(spec, B, 1 << 11)
        S, INV = DF.prime_tables_M(M, cover, B)
        good = np.array_equal(S.astype(np.int64), search.G["S"]) and np.array_equal(INV.astype(np.int64), search.G["inv"])
        print(f"  prime tables B={B}: {S.size} primes, {'identical to search.init_spec' if good else 'DIFFERENT'}", flush=True)
        ok &= good

    # 2. one retargeted BatchFeeder against the CPU feeder, variants in the order A B A C B (different N0 and numbers of rows)
    variants = {"A": (N0, U[:40]), "B": (N0 + 987654321, U[7:30]), "C": (N0 + 2 * M + 17, U[:35])}
    for B, ks, tile, llog, rg, split, f in ((32768, 14, 11, 11, 3, 2048, 0.8), (9001, 13, 11, 11, 16, 4096, 0.9)):
        log = []
        ds = DF.DeepSieve(M, cover, B, ks_log=ks, tile_log=tile, llog=llog, f=f, split=split, rg=rg, ppt=2, nthreads=64, gen_threads=32, tile_threads=64, max_rows=40, log=log.append)
        cfs = {}
        for name in "ABACB":
            n0, rows = variants[name]
            if name not in cfs:
                cfs[name] = Feeder(n0, M, rows, B=B, L=1 << llog, logK=ks, f=f, exclude=cover)
            fd = ds.feeder(n0, rows)
            assert fd is ds.fd
            for k0 in (1 << ks, 2 ** 31 + (1 << ks)):
                w = fd.window(k0)
                good = same(w, cfs[name].window(k0))
                print(f"  B={B} 2^{ks} members, {ds.n_small} small + {ds.n_large} large primes, variant {name} ({len(rows)} rows) k0={k0}: {'identical to the CPU feeder' if good else 'DIFFERENT'}", flush=True)
                ok &= good
        ok &= bool(log) and "primes below" in log[0]
        want = "staged" if os.environ.get("DEEP_STAGED") == "1" else "plain"
        good = want in log[0] and ds.fd.staged == (want == "staged")
        print(f"  the DeepSieve built the {want} large-prime kernel: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good

    # 3. deep_feeder_for keeps one DeepSieve per M (and builds a new one when M changes)
    state = {}
    logs = []
    kw = dict(B=9001, ks_log=13, tile_log=11, llog=11, f=0.9, split=4096, rg=4, max_rows=40, nthreads=64, log=logs.append)
    import deep_feeder
    orig = deep_feeder.DeepSieve.__init__
    def init(self, *a, **k):
        k.update(ppt=2, gen_threads=32, tile_threads=64)
        orig(self, *a, **k)
    deep_feeder.DeepSieve.__init__ = init
    sp_a = dict(spec, residual=U[:40])
    sp_b = dict(spec, N0=N0 + 987654321, residual=U[7:30])
    f1 = deep_feeder.deep_feeder_for(state, sp_a, **kw)
    ds1 = state["ds"]
    f2 = deep_feeder.deep_feeder_for(state, sp_b, **kw)
    good = state["ds"] is ds1 and f1 is f2 and len(logs) == 1 and f2.nU == len(sp_b["residual"])
    w = f2.window(1 << 13)
    good &= same(w, Feeder(N0 + 987654321, M, U[7:30], B=9001, L=1 << 11, logK=13, f=0.9, exclude=cover).window(1 << 13))
    print(f"  deep_feeder_for: one DeepSieve for two variants of the same M, second window identical to the CPU feeder: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    M2 = M * 7
    sp_c = dict(spec, M=M2, residual=U[:30])
    f3 = deep_feeder.deep_feeder_for(state, sp_c, **kw)
    good = state["ds"] is not ds1 and state["ds"].M == M2 and len(logs) == 2
    good &= same(f3.window(1 << 13), Feeder(N0, M2, U[:30], B=9001, L=1 << 11, logK=13, f=0.9, exclude=cover).window(1 << 13))
    print(f"  deep_feeder_for: a new M (x7: a prime dropped) builds a new DeepSieve, window identical to the CPU feeder: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good

    # 4. too many rows for the bit matrix is refused
    try:
        ds.feeder(N0, U[:50])
        good = False
    except ValueError:
        good = True
    print(f"  more rows than max_rows is refused: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

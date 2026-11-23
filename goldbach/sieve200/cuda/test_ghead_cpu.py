#!/usr/bin/env python3
"""The deep head (ghead.py, ghead_kernels.cuh) on the CPU emulation of the batch kernels (test_gbatch_cpu.py's harness): a BatchFeeder window WITH the head against the same window without it and a numpy brute force.

For every kept member of the window (chosen by the B sieve, with or without the head: the same members), a row r < head_rows leaves the list exactly when a prime s in (B, B2] divides N0 - q_r + k M; the
other rows stay, in order.  Checked: the kept members, alive_total, hm_all and hm_kept are IDENTICAL with and without the head (the statistics stay on the B sieve), cnt_acc = the old cnt, cnt / offs / rows are
the brute-force lists, the CSR is consistent, a bin capacity far too small (overflow, repeat) gives the same window, and a second call gives the same window.

    python3 test_ghead_cpu.py [--rows 40]
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB


def same_stats(a, b):
    return (np.array_equal(a.k, b.k) and np.array_equal(np.asarray(a.alive_total), np.asarray(b.alive_total)) and np.allclose(a.hm_all, b.hm_all, rtol=1e-12)
            and np.allclose(a.hm_kept, b.hm_kept, rtol=1e-12) and np.array_equal(a.block, b.block))


def brute_check(w0, w1, hrows, S2l, n0m2, mm2, U):
    """(good, removed_total): the window w1 (with the head) is w0 (without it) with, for every kept member, the rows r < hrows that a prime of S2l divides N0 - q_r + k M left out (numpy brute force)"""
    nsel = len(w0.k)
    removed_total = 0
    exp_rows, exp_cnt = [], np.zeros(nsel, dtype=np.int64)
    for i in range(nsel):
        R = np.asarray(w0.rows[w0.offs[i]:w0.offs[i + 1]]).tolist()
        kmod = int(w0.k[i]) % S2l
        keep = []
        for r in R:
            if r < hrows and bool((((n0m2 - U[r]) + kmod * mm2) % S2l == 0).any()):
                removed_total += 1
                continue
            keep.append(r)
        exp_rows.extend(keep)
        exp_cnt[i] = len(keep)
    exp_offs = np.concatenate([[0], np.cumsum(exp_cnt)])
    good = same_stats(w0, w1) and np.array_equal(np.asarray(w1.cnt_acc), np.asarray(w0.cnt)) and np.array_equal(np.asarray(w0.cnt_acc), np.asarray(w0.cnt))
    good &= np.array_equal(np.asarray(w1.cnt).astype(np.int64), exp_cnt) and np.array_equal(np.asarray(w1.offs), exp_offs)
    good &= np.array_equal(np.asarray(w1.rows), np.asarray(exp_rows, dtype=np.asarray(w1.rows).dtype))
    return bool(good), removed_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=40)
    a = ap.parse_args()
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    import gpu_sieve, gbatch, search, ghead
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec["residual"] = spec["residual"][:a.rows]
    cover = [r for r, _ in spec["cover"]]
    N0, M, U = int(spec["N0"]), int(spec["M"]), [int(q) for q in spec["residual"]]
    ok = True
    # (B, ks_log, tile_log, llog, rg, split, f, staged, rcta, stage_cap, B2, head_rows): the head primes (B, B2] must exceed the batch 2^ks
    for B, ks, tile, llog, rg, split, f, staged, rcta, stage_cap, B2, hrows in ((20011, 14, 11, 11, 4, 2048, 0.9, True, 2, 512, 150001, 12), (20011, 14, 12, 11, 3, 2048, 0.85, False, 2, 8192, 90001, 7),
                                                                                (32771, 14, 11, 11, 8, 4096, 0.9, True, 4, 512, 200003, 16)):
        search.G.clear(); search._SIEVE_CACHE.clear()
        search.init_spec(spec, B, 1 << llog)
        bf = gbatch.BatchFeeder.from_search_G(search.G, ks_log=ks, tile_log=tile, llog=llog, f=f, nthreads=64, split=split, rg=rg, ppt=2,
                                              gen_threads=max(32, -(-rcta * (1 << (ks - tile)) // 32) * 32), tile_threads=64, staged=staged, rcta=rcta, stage_cap=stage_cap)
        S2, INV2 = ghead.prime_tables_range(M, cover, B, B2)
        head = ghead.HeadStage(S2, INV2, hrows, ks, tile, rg, bf.k, threads=64)
        head.retarget(N0)
        S2l = S2.astype(np.int64)
        from deep_feeder import mod_big
        n0m2 = mod_big(N0, S2l)
        mm2 = mod_big(M, S2l)
        for k0 in (1 << ks, 2 ** 31 + (1 << ks)):
            bf.head = None
            w0 = bf.window(k0)
            bf.head = head
            w1 = bf.window(k0)
            nsel = len(w0.k)
            good, removed_total = brute_check(w0, w1, hrows, S2l, n0m2, mm2, U)
            nonvacuous = removed_total > 0 and removed_total < int(np.asarray(w0.cnt).sum())
            # a bin capacity far too small: overflow, repeat with the capacity the demand asks for; the same window; and a second call gives the same window
            head.cap = 16
            r0 = head.retries
            w2 = bf.window(k0)
            same2 = (np.array_equal(np.asarray(w2.rows), np.asarray(w1.rows)) and np.array_equal(np.asarray(w2.cnt), np.asarray(w1.cnt)) and np.array_equal(np.asarray(w2.offs), np.asarray(w1.offs))
                     and same_stats(w1, w2) and head.retries > r0)
            w3 = bf.window(k0)
            same3 = np.array_equal(np.asarray(w3.rows), np.asarray(w1.rows)) and np.array_equal(np.asarray(w3.cnt), np.asarray(w1.cnt))
            print(f"  B={B} batch 2^{ks} tile 2^{tile} rg={rg} {'STAGED rcta ' + str(rcta) if staged else 'plain'}; head: {S2.size} primes in ({B}, {B2}] on {hrows} rows, k0={k0}: {nsel} kept members, {int(np.asarray(w0.cnt).sum())} rows, "
                  f"{removed_total} removed by the head: {'identical to the brute force' if good else 'DIFFERENT'}; non-vacuous {nonvacuous}; capacity 16 -> {head.retries - r0} retries, same window {same2}; repeat {same3}", flush=True)
            ok &= good and nonvacuous and same2 and same3
    # 2. the path the driver takes: DeepSieve(head_b, head_rows) (the numpy tables of the head built from M and the cover), one BatchFeeder retargeted over variants (different N0 and number of rows: the head
    #    retargets with it), and deep_feeder_for passing head_b / head_rows through
    import deep_feeder as DF
    from deep_feeder import mod_big
    variants = {"A": (N0, U[:40]), "B": (N0 + 987654321, U[7:30]), "C": (N0 + 2 * M + 17, U[:35])}
    for B, ks, tile, llog, rg, split, f, B2, hrows in ((32768, 14, 11, 11, 3, 2048, 0.8, 120011, 10), (20011, 14, 12, 11, 8, 4096, 0.9, 80021, 20)):
        log = []
        ds = DF.DeepSieve(M, cover, B, ks_log=ks, tile_log=tile, llog=llog, f=f, split=split, rg=rg, ppt=2, nthreads=64, gen_threads=32, tile_threads=64, max_rows=40, log=log.append, head_b=B2, head_rows=hrows)
        head = ds.fd.head
        good = head is not None and head.rows == hrows and head.threads == 64 and any("deep head" in m for m in log)
        S2l = head.S.get().astype(np.int64) if hasattr(head.S, "get") else np.asarray(head.S).astype(np.int64)
        mm2 = mod_big(M, S2l)
        print(f"  DeepSieve B={B} head ({B}, {B2}]: {S2l.size} primes on {hrows} rows built: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
        for name in "ABACB":
            n0, rows = variants[name]
            fd = ds.feeder(n0, rows)
            n0m2 = mod_big(n0, S2l)
            for k0 in (1 << ks, 2 ** 31 + (1 << ks)):
                fd.head = head
                w1 = fd.window(k0)
                fd.head = None
                w0 = fd.window(k0)
                fd.head = head
                good, removed_total = brute_check(w0, w1, hrows, S2l, n0m2, mm2, rows)
                nonvacuous = removed_total > 0
                print(f"  DeepSieve B={B} variant {name} ({len(rows)} rows) k0={k0}: {len(w0.k)} kept members, {removed_total} rows removed by the head: {'identical to the brute force' if good else 'DIFFERENT'}; non-vacuous {nonvacuous}", flush=True)
                ok &= good and nonvacuous
    state, logs = {}, []
    orig = DF.DeepSieve.__init__
    def init(self, *a, **k):
        k.update(ppt=2, gen_threads=32, tile_threads=64)
        orig(self, *a, **k)
    DF.DeepSieve.__init__ = init
    f1 = DF.deep_feeder_for(state, dict(spec, residual=U[:40]), B=20011, ks_log=14, tile_log=11, llog=11, f=0.9, split=2048, rg=4, max_rows=40, nthreads=64, log=logs.append, head_b=90001, head_rows=12)
    good = f1.head is not None and f1.head.rows == 12 and any("deep head" in m for m in logs)
    f2 = DF.deep_feeder_for(state, dict(spec, N0=N0 + 987654321, residual=U[7:30]), B=20011, ks_log=14, tile_log=11, llog=11, f=0.9, split=2048, rg=4, max_rows=40, nthreads=64, log=logs.append, head_b=90001, head_rows=12)
    good &= f2 is f1 and f2.nU == 23 and sum("deep head" in m for m in logs) == 1
    state2 = {}
    f3 = DF.deep_feeder_for(state2, dict(spec, residual=U[:40]), B=20011, ks_log=14, tile_log=11, llog=11, f=0.9, split=2048, rg=4, max_rows=40, nthreads=64, log=logs.append)
    good &= f3.head is None
    DF.DeepSieve.__init__ = orig
    print(f"  deep_feeder_for passes head_b / head_rows through (one head for two variants of the same M; none without them): {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

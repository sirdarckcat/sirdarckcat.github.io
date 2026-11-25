#!/usr/bin/env python3
"""Carry-over of undecided members between pools (fround.run_pool_fused(..., stop_below, carry_state=True) + fround.carry_rows), on the CPU with
test_fround_cpu.py's stand-ins (the round kernels compiled by g++, numpy for cupy, a fake tester whose verdict depends only on (row, k)).

A sequence of pools is run twice: (A) every pool to its end, as production; (B) every pool but the last stopped at the first round that would start
with fewer than `target` active members, its undecided members prepended to the next pool with their remaining rows.  For every member the final
results must be identical: tests counted up to the first PRP (B adds the counts of the pools a member went through), PRP flag, success flag and
first-PRP row.  Also printed: rounds and tests computed of both; in B every pool but the last has no test past a first PRP (D = 1 throughout).

    python3 test_fround_carry_cpu.py
"""
import os, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_fround_cpu as T


def main():
    lib = T.build()
    cp, cupyx = T.install_fake_cupy(lib)
    import fround
    rng = np.random.default_rng(11)
    ok = True
    for p, npool, n, mean_len, target in ((0.0715, 5, 6000, 80, 1 << 12), (0.0715, 4, 3000, 400, 1 << 11), (0.2, 6, 2000, 30, 1 << 10), (0.02, 3, 2500, 150, 1 << 12)):
        pools = [T.make_pool(rng, n, mean_len=mean_len) for _ in range(npool)]
        ids = [np.arange(i * n, (i + 1) * n) for i in range(npool)]
        N = npool * n
        # (A) every pool to its end
        A = dict(tests=np.zeros(N, np.int64), prp=np.zeros(N, bool), succ=np.zeros(N, bool), frow=np.full(N, -1, np.int64))
        ra = ta = 0
        for (kv, cnt, cols), gid in zip(pools, ids):
            r = fround.run_pool_fused(T.FakeTester(p), kv, cnt, cols, target=target, dmax=8, check_range=True)
            A["tests"][gid], A["prp"][gid], A["succ"][gid], A["frow"][gid] = (np.asarray(x) for x in r[:4])
            ta += r[4]; ra += r[5]
        # (B) carry-over: stop each pool but the last when fewer than `target` members would enter a round
        B = dict(tests=np.zeros(N, np.int64), prp=np.zeros(N, bool), succ=np.zeros(N, bool), frow=np.full(N, -1, np.int64))
        rb = tb = 0
        waste_free = True
        c_kv = np.zeros(0, np.int64); c_cnt = np.zeros(0, np.int64); c_cols = np.zeros(0, np.int32); c_gid = np.zeros(0, np.int64); c_tests = np.zeros(0, np.int64)
        for i, ((kv, cnt, cols), gid) in enumerate(zip(pools, ids)):
            kv2 = np.concatenate([c_kv, kv]); cnt2 = np.concatenate([c_cnt, cnt]); cols2 = np.concatenate([c_cols, cols]).astype(np.int32)
            gid2 = np.concatenate([c_gid, gid]); prev = np.concatenate([c_tests, np.zeros(n, np.int64)])
            last_pool = i == npool - 1
            tester = T.FakeTester(p)
            r = fround.run_pool_fused(tester, kv2, cnt2, cols2, target=target, dmax=8, check_range=True, stop_below=0 if last_pool else target, carry_state=True)
            tests_m, prp_m, succ_m, frow_m, g, nl, unf, pos, last = (np.asarray(x) if hasattr(x, "shape") else x for x in r)
            tb += g; rb += nl
            done = np.ones(kv2.size, bool); done[unf] = False
            B["tests"][gid2[done]] = prev[done] + tests_m[done]
            B["prp"][gid2[done]] = prp_m[done]
            B["succ"][gid2[done]] = succ_m[done]
            B["frow"][gid2[done]] = frow_m[done]
            if not last_pool:
                waste_free &= int(g) == int(tests_m.sum())                 # every test computed was counted: none past a first PRP
            lens, cols_u = fround.carry_rows(cnt2, cols2, unf, pos)
            c_kv, c_cnt, c_cols, c_gid, c_tests = kv2[unf], np.asarray(lens), np.asarray(cols_u), gid2[unf], prev[unf] + tests_m[unf]
            assert np.all(np.asarray(prp_m)[unf] == False) and np.all(np.asarray(succ_m)[unf] == False)
        assert c_kv.size == 0
        same = all(np.array_equal(A[k], B[k]) for k in A)
        good = same and waste_free
        print(f"  p={p}, {npool} pools of {n} members, lists ~{mean_len}, target {target}: no carry {ra} rounds / {ta} tests computed, carry-over {rb} rounds / {tb} computed "
              f"(counted {int(A['tests'].sum())}); per-member results {'identical' if same else 'DIFFERENT'}; pools before the last waste-free: {waste_free}: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

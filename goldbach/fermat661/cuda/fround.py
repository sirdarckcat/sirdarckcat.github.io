"""run_pool with the bookkeeping of the Fermat rounds on the device (fround_kernels.cuh): the same per-member results, the same test lists, ~10 launches and one host read a round instead of ~100 small cupy
kernels and ~6 host syncs.

    import fround
    tests_m, prp_m, succ_m, frow, gtests, launches = fround.run_pool_fused(tester, kv, cnt, cols, target=1 << 20, dmax=8, check_range=True)

tester: MultiTester (test(idx, kv) -> uint8 flags, 1 = PRP, 0 = composite, 2 = n out of the kernel's range); kv: int64 k of every member; cnt: int64 rows of every member (0: a success without a test);
cols: int32 rows of all members, concatenated, ascending within a member (global rows of the tester's cq).  Returns what search_gpu5.run_pool returns: per member the tests counted up to its first PRP
(int64), whether a PRP was found (bool), success = every row composite (bool), the global row of the first PRP (int64, -1 none), the tests computed on the GPU and the rounds.
See fround_kernels.cuh for the round and test_fround_cpu.py for the comparison with run_pool.  The rounds are independent of the streams: run it inside a `with stream:` block (run_pool_split's halves).
"""
import os
import time

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("fr_plan", "fr_info", "fr_expand", "fr_post", "fr_compact")
_K = {}


def kernels():
    if not _K:
        mod = cp.RawModule(code=open(os.path.join(HERE, "fround_kernels.cuh")).read())
        for n in NAMES:
            _K[n] = mod.get_function(n)
    return _K


def run_pool_fused(tester, kv, cnt, cols, target=1 << 20, dmax=8, check_range=True, threads=128, profile=False):
    """profile: print run_pool's --profile-pool line (Fermat kernels timed by events, the pool's wall, the gap) for this call"""
    n = int(kv.size)
    t_prof = time.perf_counter()
    prof = [] if profile else None
    k = kernels()
    i32, i64, u8 = cp.int32, cp.int64, cp.uint8
    indptr = cp.concatenate([cp.zeros(1, i64), cp.cumsum(cnt)])
    pos = cp.zeros(n, i32)
    last = cp.full(n, -1, i32)                                  # the last row each member was tested on
    tests_m = cp.zeros(n, i32)
    prp_m = cp.zeros(n, u8)
    succ_m = (cnt == 0).astype(u8)
    frow = cp.full(n, -1, i32)
    act = cp.nonzero(cnt > 0)[0].astype(i32)                    # ascending member numbers: the order of run_pool's act
    nact = int(act.size)
    gtests = launches = 0
    if nact:
        cap = max(int(target), n) + 8                           # tests in a round: D = clamp(target // nact, 1, dmax): at most max(target, nact)
        takes, ends, keep, kcs, act2 = (cp.empty(nact, i32) for _ in range(5))
        rowsv = cp.empty(cap, i32)
        kvals = cp.empty(cap, cp.uint32)
        ctl = cp.zeros(4, i32)                                  # [0] active members entering the round, [1] error flags, [2] tests of the round, [3] spare
        ctl[0] = nact
        nb = nact                                               # the slots a round's kernels cover: an upper bound of the active members (the count entering the previous round)
        while nb > 0:
            g = (nb + threads - 1) // threads
            k["fr_plan"]((g,), (threads,), (act, cnt, pos, ctl, np.int32(nb), np.int32(target), np.int32(dmax), takes))
            cp.cumsum(takes[:nb], dtype=i32, out=ends[:nb])
            k["fr_info"]((1,), (1,), (ends, np.int32(nb), ctl))
            c = cp.asnumpy(ctl[:3])                             # the round's one host read: (active members, error flags, tests)
            nact_now, err, total = int(c[0]), int(c[1]), int(c[2])
            if err & 1:
                raise RuntimeError("a member's rows are not tested in ascending order")
            if err & 2:
                raise RuntimeError("kernel 28 flagged an n outside its range")
            if nact_now == 0:
                break
            k["fr_expand"](((total + threads - 1) // threads,), (threads,), (act, ends, takes, indptr, pos, cols, kv, np.int32(nb), np.int32(total), rowsv, kvals))
            if prof is not None:
                e0 = cp.cuda.Event(); e1 = cp.cuda.Event(); e0.record()
            flags = tester.test(rowsv[:total], kvals[:total])
            if prof is not None:
                e1.record(); prof.append((e0, e1, total))
            k["fr_post"]((g,), (threads,), (act, ends, takes, rowsv, flags, pos, last, cnt, tests_m, prp_m, succ_m, frow, keep, ctl, np.int32(nb), np.int32(1 if check_range else 0)))
            cp.cumsum(keep[:nb], dtype=i32, out=kcs[:nb])
            k["fr_compact"]((g,), (threads,), (act, keep, kcs, act2, ctl, np.int32(nb)))
            act, act2 = act2, act
            gtests += total
            launches += 1
            nb = nact_now
    if prof is not None:
        cp.cuda.Device().synchronize()
        wall = time.perf_counter() - t_prof
        kern = sum(cp.cuda.get_elapsed_time(a, b) for a, b, _ in prof) / 1e3
        print(f"[profile-pool] [fused rounds] {n} members, {launches} rounds, {gtests} tests: Fermat kernels {kern:.3f} s on the GPU, run_pool wall {wall:.3f} s, gap {wall - kern:.3f} s "
              f"({100 * (wall - kern) / max(wall, 1e-9):.1f}% of run_pool); {gtests / max(kern, 1e-9) / 1e6:.1f}M tests/s while a kernel runs, {gtests / max(wall, 1e-9) / 1e6:.1f}M over the pool", flush=True)
    return tests_m.astype(i64), prp_m.astype(cp.bool_), succ_m.astype(cp.bool_), frow.astype(i64), gtests, launches

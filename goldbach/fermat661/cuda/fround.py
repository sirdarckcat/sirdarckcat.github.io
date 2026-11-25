"""run_pool with the bookkeeping of the Fermat rounds on the device (fround_kernels.cuh): the same per-member results, the same test lists, ~10 launches and one host read a round instead of ~100 small cupy
kernels and ~6 host syncs.

    import fround
    tests_m, prp_m, succ_m, frow, gtests, launches = fround.run_pool_fused(tester, kv, cnt, cols, target=1 << 20, dmax=8, check_range=True)

tester: MultiTester (test(idx, kv) -> uint8 flags, 1 = PRP, 0 = composite, 2 = n out of the kernel's range); kv: int64 k of every member; cnt: int64 rows of every member (0: a success without a test);
cols: int32 rows of all members, concatenated, ascending within a member (global rows of the tester's cq).  Returns what search_gpu5.run_pool returns: per member the tests counted up to its first PRP
(int64), whether a PRP was found (bool), success = every row composite (bool), the global row of the first PRP (int64, -1 none), the tests computed on the GPU and the rounds.
See fround_kernels.cuh for the round and test_fround_cpu.py for the comparison with run_pool.  The rounds are independent of the streams: run it inside a `with stream:` block (run_pool_split's halves).
"""
import contextlib
import os
import threading
import time

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("fr_plan", "fr_info", "fr_expand", "fr_post", "fr_compact")
_K = {}
_LOCK = threading.Lock()                                        # run_pool_split's two threads call this first at the same time


def kernels():
    with _LOCK:
        if not _K:
            mod = cp.RawModule(code=open(os.path.join(HERE, "fround_kernels.cuh")).read())
            for n in NAMES:
                _K[n] = mod.get_function(n)
    return _K


def run_pool_fused(tester, kv, cnt, cols, target=1 << 20, dmax=8, check_range=True, threads=128, profile=False, ctl_stream=None, stop_below=0, carry_state=False):
    """profile: print run_pool's --profile-pool line (Fermat kernels timed by events, the pool's wall, the gap) for this call.
    ctl_stream: a CUDA stream (or None).  With one, the round's BOOKKEEPING (the five kernels, the two scans, the host read of ctl) runs on it and only the Fermat kernel (tester.test) runs on the caller's
    current stream, with events ordering the two (the bookkeeping waits for the test, the test waits for fr_expand).  Why: beside a sieve that owns the highest stream priority the pool's stream is the lowest, and
    each of a round's ~8 small kernels waits for an SM slot that the sieve's queued CTAs take first (measured by the GPU session with --profile-pool: the gap of a half-pool of 36-41 rounds beside the sieve is
    0.24-0.30 s = 6-8 ms a round; expected 0.2-0.3 ms a round alone, not measured for the fused rounds); a control stream ABOVE the sieve's priority (FERMAT_CTL_PRIORITY=-100 = the greatest, the sieve at
    OVERLAP_SIEVE_PRIORITY=-4) places those kernels at the next free slot while the long Fermat kernel keeps the pool's low priority.  Same results; what it gains on a GPU is not measured.
    stop_below (carry-over, costside/RESULTS.md): stop the pool at the first round that would start with fewer than stop_below active members (0: run to the end, as before), so that every
    round is a full one (D = 1 when stop_below >= target, no tail of small launches, no test past a first PRP).  The members left undecided keep their rows tested so far; with carry_state=True the
    return value has three more entries: unf (int64, the undecided members, ascending), pos (int64, rows of each member tested so far) and last (int64, the last row tested, -1 none), from which
    carry_rows() makes their remaining lists for the next pool.  Their tests_m / frow so far are in the first entries (tests counted up to now, frow -1); prp_m and succ_m are False for them."""
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
        bk = contextlib.nullcontext()                           # where the bookkeeping runs: the caller's current stream, or ctl_stream
        if ctl_stream is not None:
            cur = cp.cuda.get_current_stream()
            ev_in, ev_x, ev_t = (cp.cuda.Event(disable_timing=True) for _ in range(3))      # re-recorded every round: a wait captures the record it was issued after
            ev_in.record(cur)
            ctl_stream.wait_event(ev_in)                        # kv, cnt, cols, indptr and the work arrays are complete before the control stream reads them
            bk = ctl_stream
        while nb > 0:
            with bk:
                g = (nb + threads - 1) // threads
                k["fr_plan"]((g,), (threads,), (act, cnt, pos, ctl, np.int32(nb), np.int32(target), np.int32(dmax), takes))
                cp.cumsum(takes[:nb], dtype=i32, out=ends[:nb])
                k["fr_info"]((1,), (1,), (ends, np.int32(nb), ctl))
                c = cp.asnumpy(ctl[:3])                         # the round's one host read: (active members, error flags, tests)
                nact_now, err, total = int(c[0]), int(c[1]), int(c[2])
                if err & 1:
                    raise RuntimeError("a member's rows are not tested in ascending order")
                if err & 2:
                    raise RuntimeError("kernel 28 flagged an n outside its range")
                if nact_now == 0 or nact_now < stop_below:
                    break
                k["fr_expand"](((total + threads - 1) // threads,), (threads,), (act, ends, takes, indptr, pos, cols, kv, np.int32(nb), np.int32(total), rowsv, kvals))
                if ctl_stream is not None:
                    ev_x.record(ctl_stream)
            if ctl_stream is not None:
                cur.wait_event(ev_x)                            # the Fermat kernel starts after fr_expand
            if prof is not None:
                e0 = cp.cuda.Event(); e1 = cp.cuda.Event(); e0.record()
            flags = tester.test(rowsv[:total], kvals[:total])
            if prof is not None:
                e1.record(); prof.append((e0, e1, total))
            if ctl_stream is not None:
                ev_t.record(cur)
                ctl_stream.wait_event(ev_t)                     # fr_post reads the flags: after the Fermat kernel
            with bk:
                k["fr_post"]((g,), (threads,), (act, ends, takes, rowsv, flags, pos, last, cnt, tests_m, prp_m, succ_m, frow, keep, ctl, np.int32(nb), np.int32(1 if check_range else 0)))
                cp.cumsum(keep[:nb], dtype=i32, out=kcs[:nb])
                k["fr_compact"]((g,), (threads,), (act, keep, kcs, act2, ctl, np.int32(nb)))
            act, act2 = act2, act
            gtests += total
            launches += 1
            nb = nact_now
        if ctl_stream is not None:
            ev_f = cp.cuda.Event(disable_timing=True)
            ev_f.record(ctl_stream)
            cur.wait_event(ev_f)                                # the caller's stream sees the results (tests_m, prp_m, succ_m, frow) only after the last bookkeeping kernel (the host read that ends
                                                                    # the loop already follows them: this keeps the rule 'a stream's results are complete for its next launch' without that argument)
    if prof is not None:
        cp.cuda.Device().synchronize()
        wall = time.perf_counter() - t_prof
        kern = sum(cp.cuda.get_elapsed_time(a, b) for a, b, _ in prof) / 1e3
        print(f"[profile-pool] [fused rounds] {n} members, {launches} rounds, {gtests} tests: Fermat kernels {kern:.3f} s on the GPU, run_pool wall {wall:.3f} s, gap {wall - kern:.3f} s "
              f"({100 * (wall - kern) / max(wall, 1e-9):.1f}% of run_pool); {gtests / max(kern, 1e-9) / 1e6:.1f}M tests/s while a kernel runs, {gtests / max(wall, 1e-9) / 1e6:.1f}M over the pool", flush=True)
    res = (tests_m.astype(i64), prp_m.astype(cp.bool_), succ_m.astype(cp.bool_), frow.astype(i64), gtests, launches)
    if not carry_state:
        return res
    nleft = int(cp.asnumpy(ctl[:1])[0]) if nact else 0           # the active members entering the round that was not run (0 when the pool ran to its end)
    unf = cp.sort(act[:nleft].astype(i64)) if nleft else cp.zeros(0, i64)
    return res + (unf, pos.astype(i64), last.astype(i64))


def carry_rows(cnt, cols, unf, pos):
    """The remaining row lists of the undecided members unf of a pool (cnt, cols as given to run_pool_fused, pos from its carry_state): (cnt_rem int64, cols_rem int32), in the order of unf."""
    i64 = cp.int64
    if int(unf.size) == 0:
        return cp.zeros(0, i64), cp.zeros(0, cp.int32)
    indptr = cp.concatenate([cp.zeros(1, i64), cp.cumsum(cnt.astype(i64))])
    pos_u = pos[unf]
    lens = cnt.astype(i64)[unf] - pos_u
    offs = cp.cumsum(lens)
    total = int(offs[-1])
    seg = cp.searchsorted(offs, cp.arange(total), side="right")
    cols_u = cols[(indptr[unf] + pos_u)[seg] + (cp.arange(total) - (offs - lens)[seg])]
    return lens, cols_u.astype(cp.int32)

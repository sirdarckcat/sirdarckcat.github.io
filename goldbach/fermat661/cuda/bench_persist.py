#!/usr/bin/env python3
"""On a GPU: the persistent pool kernel (fermat28_persist_kernel.cuh) against the production Fermat kernel, KERNEL time only: no driver, no sieve, no host work between rounds.

    python3 bench_persist.py [--variant s1r_asm|s1rw] [--sync 0 1] [--members 400000] [--list 300] [--rows 20000] [--sieve 20000] [--check 2000] [--reps 3]
                             [--cta-sm 0] [--prod-tests 8388608] [--maxreg 0]

Why: plt8 (GPU session, 23 Nov 2026 10:21Z) measured the first persistent kernel ~1 s a batch SLOWER than the round-based path (2.7 s against 1.84 s) although its step loop is the production
loop (same SASS); the diagnosis is a warp that splits when a few lanes fetch a new member (fermat28_persist_kernel.cuh, "WARP CONVERGENCE").  This isolates the kernel:
  1. the production kernel on --prod-tests random rows: tests/s, the figure a persistent kernel has to match (the RTX PRO 6000's 23.3M tests/s);
  2. the persistent kernel on a pool of --members members of --list rows each, once per --sync value (0: no __syncwarp, the first version; 1: __syncwarp before each test): kernel
     milliseconds, tests done in them, tests/s, the members left in flight when the queue emptied (the caller's round-based path would finish those), and the ratio to 1.
The pool is synthetic: --rows distinct random odd 661-bit numbers with no prime factor below --sieve (so ~4% of them are primes: ~26 tests a member before its first PRP; plt8's real pools
have ~7% and 14), n = cq row (M = 0, k = 0), each member a list of --list rows drawn at random.  --check N compares the first N members' results with the production kernel's flags on the
same rows (tests = index of the first PRP + 1, the row, the state); a mismatch is printed as WRONG and the exit code is 1.
"""
import argparse, os, random, sys, time
import numpy as np
import cupy as cp
import gmpy2
from gmpy2 import mpz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpu_fermat28 as g28

VARIANTS = {
    "s1r_asm": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True),       # the RTX PRO 6000s' production kernel
    "s1rw": dict(step_file="fermat28_step_s1rw.cuh"),                       # A100 / L4 / T4
}


def primes_below(n):
    s = bytearray([1]) * n
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n) if s[i]]


def make_rows(count, sieve, seed):
    """`count` random odd 661-bit numbers with no prime factor below `sieve`"""
    rnd = random.Random(seed)
    P = mpz(1)
    for p in primes_below(sieve):
        P *= p
    rows = []
    while len(rows) < count:
        n = mpz(rnd.getrandbits(660)) | (mpz(1) << 660) | 1
        if gmpy2.gcd(n, P) == 1:
            rows.append(n)
    return rows


def run_persist(kp, regs, CQ, M, kv, cnt, indptr, cols, cta_sm, threads=128):
    n = int(kv.size)
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    grid = min(nsm * (cta_sm or g28.persist_ctas_per_sm(regs, threads)), -(-n // threads))
    counter = cp.zeros(1, dtype=cp.int32)
    tests = cp.empty(n, dtype=cp.int32)
    state = cp.empty(n, dtype=cp.uint8)
    frow = cp.empty(n, dtype=cp.int32)
    e0, e1 = cp.cuda.Event(), cp.cuda.Event()
    e0.record()
    kp((grid,), (threads,), (CQ, M, kv, cnt, indptr, cols, np.int32(n), counter, tests, state, frow))
    e1.record()
    e1.synchronize()
    return cp.cuda.get_elapsed_time(e0, e1), grid, tests, state, frow


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="s1r_asm", choices=sorted(VARIANTS))
    ap.add_argument("--sync", nargs="+", default=["0", "1"], choices=("0", "1"))
    ap.add_argument("--members", type=int, default=400000)
    ap.add_argument("--list", type=int, default=300, dest="llen")
    ap.add_argument("--rows", type=int, default=20000)
    ap.add_argument("--sieve", type=int, default=20000)
    ap.add_argument("--check", type=int, default=2000)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--cta-sm", type=int, default=0)
    ap.add_argument("--prod-tests", type=int, default=1 << 23)
    ap.add_argument("--maxreg", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    kopts = dict(VARIANTS[a.variant])
    if a.maxreg:
        kopts["maxreg"] = a.maxreg
    try:
        name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    except Exception:
        name = "?"
    print(f"device {name}: {a.members} members x {a.llen} rows from {a.rows} distinct rows (no prime factor below {a.sieve}), variant {a.variant}", flush=True)
    t0 = time.perf_counter()
    rows = make_rows(a.rows, a.sieve, a.seed)
    CQ = cp.asarray(np.stack([g28.to_limbs(int(n)) for n in rows]))
    M = cp.zeros(21, dtype=cp.uint32)
    rng = np.random.default_rng(a.seed)
    cols = cp.asarray(rng.integers(0, a.rows, a.members * a.llen).astype(np.int32))
    cnt = cp.full(a.members, a.llen, dtype=cp.int32)
    indptr = cp.arange(a.members + 1, dtype=cp.int64) * a.llen
    kv = cp.zeros(a.members, dtype=cp.uint32)
    print(f"  pool built in {time.perf_counter() - t0:.1f} s", flush=True)
    ok = True
    # 1. the production kernel
    kprod = g28.kernel(21, **kopts)
    T = a.prod_tests
    idx = cp.asarray(rng.integers(0, a.rows, T).astype(np.int32))
    kz = cp.zeros(T, dtype=cp.uint32)
    out = cp.empty(T, dtype=cp.uint8)
    launch = lambda: kprod(((T + 127) // 128,), (128,), (CQ, M, idx, kz, out, np.int32(T)))
    launch()                                                                    # compile + warm up
    cp.cuda.Device().synchronize()
    best = None
    for _ in range(a.reps):
        e0, e1 = cp.cuda.Event(), cp.cuda.Event()
        e0.record()
        launch()
        e1.record()
        e1.synchronize()
        ms = cp.cuda.get_elapsed_time(e0, e1)
        best = ms if best is None else min(best, ms)
    prod_rate = T / best / 1e3
    print(f"  production kernel: {T} tests in {best:.1f} ms = {prod_rate:.2f}M tests/s (best of {a.reps}), {kprod.attributes['num_regs']} registers, {100 * float((out == 1).sum()) / T:.2f}% probable primes", flush=True)
    # 2. the persistent kernel
    ncheck = min(a.check, a.members)
    if ncheck:
        flags = cp.empty(ncheck * a.llen, dtype=cp.uint8)
        kprod(((ncheck * a.llen + 127) // 128,), (128,), (CQ, M, cols[:ncheck * a.llen], cp.zeros(ncheck * a.llen, dtype=cp.uint32), flags, np.int32(ncheck * a.llen)))
        flags = cp.asnumpy(flags).reshape(ncheck, a.llen)
        has = (flags == 1).any(axis=1)
        first = np.argmax(flags == 1, axis=1)
        cols_h = cp.asnumpy(cols[:ncheck * a.llen]).reshape(ncheck, a.llen)
    for sync in a.sync:
        os.environ["FERMAT_PERSIST_SYNC"] = sync
        kp = g28.persist_kernel(21, **kopts)
        regs = kp.attributes["num_regs"]
        run_persist(kp, regs, CQ, M, kv[:min(a.members, 4096)], cnt[:min(a.members, 4096)], indptr[:min(a.members, 4096) + 1], cols, a.cta_sm)   # compile + warm up
        cp.cuda.Device().synchronize()
        best = None
        for _ in range(a.reps):
            ms, grid, tests, state, frow = run_persist(kp, regs, CQ, M, kv, cnt, indptr, cols, a.cta_sm)
            if best is None or ms < best[0]:
                best = (ms, grid, tests, state, frow)
        ms, grid, tests, state, frow = best
        tests_h, state_h = cp.asnumpy(tests).astype(np.int64), cp.asnumpy(state)
        done = int(tests_h.sum())
        left = int((state_h == 0).sum())
        rate = done / ms / 1e3
        wrong = 0
        if ncheck:
            st, te, fr = state_h[:ncheck], tests_h[:ncheck], cp.asnumpy(frow[:ncheck])
            fin = st != 0
            exp_t = np.where(has, first + 1, a.llen)
            exp_s = np.where(has, 1, 2)
            exp_f = np.where(has, cols_h[np.arange(ncheck), first], -1)
            wrong = int((fin & ((te != exp_t) | (st != exp_s) | (fr != exp_f))).sum())
            for i in np.nonzero(~fin)[0]:                                       # left to the caller: the rows it did are all composite
                wrong += int(not (te[i] <= a.llen and not (flags[i, :te[i]] == 1).any()))
        print(f"  persistent kernel, sync {sync}: grid {grid} x 128 ({grid // cp.cuda.Device().attributes['MultiProcessorCount']} CTAs/SM, {regs} registers): {ms:.1f} ms for {done} tests "
              f"({done / a.members:.1f} a member) = {rate:.2f}M tests/s = {rate / prod_rate:.2f} x the production kernel; {left} members in flight when the queue emptied; "
              f"{'results identical to the production kernel on ' + str(ncheck) + ' members' if wrong == 0 else 'WRONG: ' + str(wrong) + ' of ' + str(ncheck) + ' members differ'}", flush=True)
        ok &= wrong == 0
    print("BENCH-PERSIST-DONE" if ok else "BENCH-PERSIST-WRONG", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

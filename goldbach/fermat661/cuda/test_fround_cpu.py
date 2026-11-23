#!/usr/bin/env python3
"""fround.run_pool_fused (the Fermat rounds' bookkeeping as device kernels, fround_kernels.cuh) against the driver's run_pool, on random pools, on the CPU.

The kernels are compiled from the same .cuh by g++ (fround_cpu.cpp: loops over blocks and threads), cupy is a numpy stand-in, the Fermat tester is a fake (a hash of (row, k) decides PRP / composite / out of range).
The reference is run_pool VERBATIM from the GPU session's search_gpu5.py (origin/ccr-8ffe9d7a-4ni11u @123d93c, 23 Nov 2026), exec'd with the same fake cupy.  Compared for every pool:
tests counted, PRP flags, successes, first-PRP rows, the tests computed on the GPU and the number of rounds (all identical), for several (target, dmax), pools with empty lists and one-row lists,
PRP probabilities from 0 to 1, and the two errors (rows not ascending; a flag above 1 with kernel 28's range check, and ignored without it).

    python3 test_fround_cpu.py
"""
import ctypes, os, subprocess, sys, time, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

REF = r'''
def run_pool(tester, kv, cnt, cols, target=None):
    n = int(kv.size)
    prof = [] if args.profile_pool else None
    t_prof = time.perf_counter()
    indptr = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
    frow = cp.full(n, -1, cp.int64)
    last = cp.full(n, -1, cp.int64)                            # the last row each member was tested on
    tests_m = cp.zeros(n, cp.int64)
    prp_m = cp.zeros(n, cp.bool_)
    succ_m = cnt == 0
    act = cp.nonzero(cnt > 0)[0]
    pos = cp.zeros(n, cp.int64)
    gtests = launches = 0
    while act.size:
        rem = cnt[act] - pos[act]
        D = int(max(1, min(args.dmax, int(rem.max()), (args.target if target is None else target) // int(act.size))))
        take = cp.minimum(rem, D)
        csum = cp.cumsum(take)
        total = int(csum[-1])
        m_of = cp.searchsorted(csum, cp.arange(total), side="right")
        off = cp.arange(total) - (csum - take)[m_of]
        ip = (indptr[act] + pos[act])[m_of] + off
        rowsv = cols[ip]
        flags = tester.test(rowsv, kv[act][m_of].astype(cp.uint32))
        prev = last[act][m_of]                                  # the row before each tested row: the member's last row, or the one before it here
        if total > 1:
            same = m_of[1:] == m_of[:-1]
            prev[1:] = cp.where(same, rowsv[:-1].astype(cp.int64), prev[1:])
        bad = (rowsv.astype(cp.int64) <= prev).any()
        if args.kernel == 28:
            bad = bad | ((flags > 1).any() * 2)
        bad = int(bad)
        if bad & 1:
            raise RuntimeError("a member's rows are not tested in ascending order")
        if bad & 2:
            raise RuntimeError("kernel 28 flagged an n outside its range")
        last[act] = rowsv[csum - 1].astype(cp.int64)
        big = D + 1
        first = cp.full(int(act.size), big, dtype=cp.int32)          # scatter_min: no int64
        cupyx.scatter_min(first, m_of, cp.where(flags == 1, off, big).astype(cp.int32))
        hit = first < big
        tests_m[act] += cp.where(hit, first.astype(cp.int64) + 1, take)
        prp_m[act[hit]] = True
        frow[act[hit]] = rowsv[(csum - take)[hit] + first[hit].astype(cp.int64)].astype(cp.int64)
        pos[act] += take
        done = (~hit) & (pos[act] == cnt[act])
        succ_m[act[done]] = True
        act = act[(~hit) & (~done)]
        gtests += total
        launches += 1
    return tests_m, prp_m, succ_m, frow, gtests, launches
'''


def build():
    so = os.path.join(HERE, "libfround_cpu.so")
    src = [os.path.join(HERE, f) for f in ("fround_cpu.cpp", "fround_kernels.cuh")]
    if not os.path.exists(so) or os.path.getmtime(so) < max(os.path.getmtime(s) for s in src):
        subprocess.run(["g++", "-O2", "-shared", "-fPIC", "-o", so, src[0]], check=True, cwd=HERE)
    return ctypes.CDLL(so)


class FakeKernel:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, grid, block, args, shared_mem=0):
        conv = []
        for a in args:
            if isinstance(a, np.ndarray):
                assert a.flags["C_CONTIGUOUS"], "kernel arguments must be contiguous"
                conv.append(ctypes.c_void_p(a.ctypes.data))
            elif isinstance(a, (np.integer, int)):
                conv.append(ctypes.c_int(int(a)))
            else:
                raise TypeError(type(a))
        self.fn(ctypes.c_int(int(grid[0])), ctypes.c_int(int(block[0])), *conv)


def install_fake_cupy(lib):
    cp = types.ModuleType("cupy")
    cp.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
    cp.asnumpy = np.asarray

    class RawModule:
        def __init__(self, code=None, options=()):
            self.code = code

        def get_function(self, name):
            return FakeKernel(getattr(lib, "cpu_" + name))
    cp.RawModule = RawModule
    cupyx = types.ModuleType("cupyx")
    cupyx.scatter_min = lambda a, idx, v: np.minimum.at(a, idx, v)
    sys.modules["cupy"] = cp
    sys.modules["cupyx"] = cupyx
    return cp, cupyx


class FakeTester:
    """flag(row, k): 1 with probability p (a hash), 2 for the (row, k) pairs of `range_bad`; the rows are global rows."""
    def __init__(self, p, range_bad=0.0):
        self.p, self.range_bad, self.tests = p, range_bad, 0

    def test(self, idx, kv):
        assert idx.dtype == np.int32 and kv.dtype == np.uint32 and idx.size == kv.size
        self.tests += int(idx.size)
        h = ((idx.astype(np.uint64) * np.uint64(0x9E3779B1) + kv.astype(np.uint64) * np.uint64(0x85EBCA6B) + np.uint64(12345)) * np.uint64(0xC2B2AE35)) >> np.uint64(11)
        u = (h % np.uint64(1000003)).astype(np.float64) / 1000003.0
        out = (u < self.p).astype(np.uint8)
        if self.range_bad:
            out[(u > 1.0 - self.range_bad)] = 2
        return out


def make_pool(rng, n, R=1248, mean_len=60, zero_frac=0.01, unsorted=0):
    cnt = np.minimum(rng.geometric(1.0 / mean_len, n), R).astype(np.int64)
    cnt[rng.random(n) < zero_frac] = 0
    cnt[rng.random(n) < 0.02] = 1
    parts = []
    for c in cnt:
        parts.append(np.sort(rng.choice(R, int(c), replace=False)).astype(np.int32) if c else np.zeros(0, np.int32))
    cols = np.concatenate(parts).astype(np.int32)
    if unsorted:                                               # swap two neighbouring rows of `unsorted` members with at least 3 rows
        offs = np.concatenate([[0], np.cumsum(cnt)])
        for m in np.nonzero(cnt >= 3)[0][:unsorted]:
            a = offs[m] + 1
            cols[a], cols[a + 1] = cols[a + 1], cols[a]
    kv = rng.integers(1 << 21, 1 << 24, n).astype(np.int64)
    return kv, cnt, cols


def main():
    lib = build()
    cp, cupyx = install_fake_cupy(lib)
    import fround
    args = types.SimpleNamespace(dmax=8, target=1 << 20, profile_pool=0, kernel=28)
    ns = dict(cp=cp, cupyx=cupyx, np=np, args=args, time=time)
    exec(REF, ns)
    ref = ns["run_pool"]
    rng = np.random.default_rng(5)
    ok = True

    def same(a, b):
        return all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(a[:4], b[:4])) and a[4] == b[4] and a[5] == b[5]

    cases = []
    for p, n, mean_len in ((0.0715, 20000, 60), (0.0715, 6000, 400), (0.3, 5000, 20), (0.0, 800, 12), (1.0, 800, 12), (0.02, 3000, 150)):
        cases.append((p, n, mean_len))
    for p, n, mean_len in cases:
        kv, cnt, cols = make_pool(rng, n, mean_len=mean_len)
        for target, dmax in ((1 << 20, 8), (1 << 12, 8), (1 << 10, 3), (1 << 14, 1), (1 << 20, 16)):
            args.dmax, args.target = dmax, target
            t1, t2 = FakeTester(p), FakeTester(p)
            a = ref(t1, kv, cnt, cols)
            b = fround.run_pool_fused(t2, kv, cnt, cols, target=target, dmax=dmax, check_range=True)
            good = same(a, b) and t1.tests == t2.tests
            nsucc, nprp = int(np.asarray(a[2]).sum()), int(np.asarray(a[1]).sum())
            print(f"  p={p} n={n} lists ~{mean_len} target 2^{target.bit_length() - 1} dmax {dmax}: {a[5]} rounds, {a[4]} tests computed ({int(np.asarray(a[0]).sum())} counted), {nprp} PRP, {nsucc} successes: "
                  f"{'identical' if good else 'DIFFERENT'}", flush=True)
            ok &= good and (nsucc + nprp == n)
    # the split's halves: target // 2 and a slice of the pool (kv / cnt / cols sliced at a member boundary)
    kv, cnt, cols = make_pool(rng, 9000, mean_len=80)
    offs = np.concatenate([[0], np.cumsum(cnt)])
    mid = 4500
    for part in ((0, mid), (mid, 9000)):
        a0, b0 = part
        sl = (kv[a0:b0], cnt[a0:b0], cols[offs[a0]:offs[b0]])
        args.dmax, args.target = 8, 1 << 20
        r = ref(FakeTester(0.0715), *sl, target=(1 << 20) // 2)
        f = fround.run_pool_fused(FakeTester(0.0715), *sl, target=(1 << 20) // 2, dmax=8, check_range=True)
        good = same(r, f)
        print(f"  a half of a pool ({b0 - a0} members, target 2^19): {'identical' if good else 'DIFFERENT'}", flush=True)
        ok &= good
    # errors: rows not ascending (both raise, or neither if no tested block holds the pair), a flag above 1 (kernel 28's range check) and ignored without it
    kv, cnt, cols = make_pool(rng, 3000, mean_len=60, unsorted=3)
    args.dmax, args.target = 8, 1 << 12
    outs = []
    for fn in (lambda: ref(FakeTester(0.0715), kv, cnt, cols), lambda: fround.run_pool_fused(FakeTester(0.0715), kv, cnt, cols, target=1 << 12, dmax=8, check_range=True)):
        try:
            fn()
            outs.append("no error")
        except RuntimeError as e:
            outs.append(str(e))
    good = outs[0] == outs[1] == "a member's rows are not tested in ascending order"
    print(f"  rows not ascending: run_pool says {outs[0]!r}, fused says {outs[1]!r}: {'ok' if good else 'DIFFERENT'}", flush=True)
    ok &= good
    kv, cnt, cols = make_pool(rng, 3000, mean_len=60)
    outs = []
    for fn in (lambda: ref(FakeTester(0.0715, range_bad=0.001), kv, cnt, cols), lambda: fround.run_pool_fused(FakeTester(0.0715, range_bad=0.001), kv, cnt, cols, target=1 << 12, dmax=8, check_range=True)):
        try:
            fn()
            outs.append("no error")
        except RuntimeError as e:
            outs.append(str(e))
    good = outs[0] == outs[1] == "kernel 28 flagged an n outside its range"
    print(f"  a flag above 1 with kernel 28: run_pool says {outs[0]!r}, fused says {outs[1]!r}: {'ok' if good else 'DIFFERENT'}", flush=True)
    ok &= good
    args.kernel = 3                                            # other kernels: flags above 1 are not checked (and are no PRP)
    r = ref(FakeTester(0.0715, range_bad=0.001), kv, cnt, cols)
    f = fround.run_pool_fused(FakeTester(0.0715, range_bad=0.001), kv, cnt, cols, target=1 << 12, dmax=8, check_range=False)
    good = same(r, f)
    print(f"  a flag above 1 without the range check (kernel 3 / 2): {'identical' if good else 'DIFFERENT'}", flush=True)
    ok &= good
    # nothing to do
    z = fround.run_pool_fused(FakeTester(0.1), np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0, np.int32), target=1 << 12, dmax=8)
    zc = fround.run_pool_fused(FakeTester(0.1), np.arange(5, dtype=np.int64), np.zeros(5, np.int64), np.zeros(0, np.int32), target=1 << 12, dmax=8)
    good = z[4] == 0 and z[5] == 0 and zc[2].all() and zc[4] == 0
    print(f"  empty pool; a pool of members without rows (all successes, no test): {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

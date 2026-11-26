#!/usr/bin/env python3
"""fround.run_pool_fused (the Fermat rounds' bookkeeping as device kernels, fround_kernels.cuh) against the driver's run_pool, on random pools, on the CPU.

The kernels are compiled from the same .cuh by g++ (fround_cpu.cpp: loops over blocks and threads), cupy is a numpy stand-in, the Fermat tester is a fake (a hash of (row, k) decides PRP / composite / out of range).
The reference is run_pool VERBATIM from the GPU session's search_gpu5.py (origin/ccr-8ffe9d7a-4ni11u @123d93c, 23 Nov 2026), exec'd with the same fake cupy.  Compared for every pool:
tests counted, PRP flags, successes, first-PRP rows, the tests computed on the GPU and the number of rounds (all identical), for several (target, dmax), pools with empty lists and one-row lists,
PRP probabilities from 0 to 1, and the two errors (rows not ascending; a flag above 1 with kernel 28's range check, and ignored without it).
The control-stream mode (run_pool_fused(..., ctl_stream=s): the round's bookkeeping on a second stream, only the Fermat kernel on the caller's) runs against a fake device that records every launch with
its stream and every event record / wait: the results are identical, the launches of the two streams form ONE chain (each launch happens after the one issued before it, through the events and the host
read: no kernel can overlap another or read a half-written array), the launch order per round is the expected one, and a run with the waits left out is caught by the same checker.

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


class FakeEvent:
    def __init__(self, dev):
        self.dev, self.op = dev, None

    def record(self, stream=None):
        self.op = self.dev.issue("event", stream)


class FakeStream:
    """a stream of the fake device; `with s:` makes it the current one; wait_event makes the NEXT launch on it depend on the event's record"""
    def __init__(self, dev, name):
        self.dev, self.name, self.last, self.waits = dev, name, None, []

    def __enter__(self):
        self.dev.stack.append(self)
        return self

    def __exit__(self, *exc):
        assert self.dev.stack.pop() is self
        return False

    def wait_event(self, ev):
        assert ev.op is not None, "waiting for an event that was never recorded"
        if not self.dev.ignore_waits:
            self.waits.append(ev.op)


class FakeDevice:
    """every launch (kernel, cumsum, host read, event record) is an op with the ops it must follow: the previous op of its stream, the events it waits for, and the last host read (the host issues
    it after a synchronous read returned, and that read follows everything the stream had before it)"""
    def __init__(self):
        self.ignore_waits = False
        self.reset()

    def reset(self):
        self.cur = FakeStream(self, "cur")
        self.stack = [self.cur]
        self.ops = []
        self.host_barrier = None

    def current(self):
        return self.stack[-1]

    def issue(self, name, stream=None, host_sync=False):
        st = stream if stream is not None else self.current()
        preds = list(st.waits)
        st.waits = []
        if st.last is not None:
            preds.append(st.last)
        if self.host_barrier is not None:
            preds.append(self.host_barrier)
        self.ops.append((name, st.name, preds))
        st.last = len(self.ops) - 1
        if host_sync:
            self.host_barrier = st.last
        return st.last


DEV = FakeDevice()


class FakeKernel:
    def __init__(self, fn, name="kernel"):
        self.fn, self.name = fn, name

    def __call__(self, grid, block, args, shared_mem=0):
        DEV.issue(self.name)
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
    cp.asnumpy = lambda a: (DEV.issue("host_read", host_sync=True), np.asarray(a))[1]
    cp.cumsum = lambda *a, **k: (DEV.issue("cumsum"), np.cumsum(*a, **k))[1]
    cp.cuda = types.SimpleNamespace(Event=lambda *a, **k: FakeEvent(DEV), get_current_stream=lambda: DEV.current(), get_elapsed_time=lambda a, b: 1.0,
                                    Device=lambda *a: types.SimpleNamespace(synchronize=lambda: None, id=0))

    class RawModule:
        def __init__(self, code=None, options=()):
            self.code = code

        def get_function(self, name):
            return FakeKernel(getattr(lib, "cpu_" + name), name)
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
        DEV.issue("test")
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
    # the control-stream mode: the bookkeeping on a second stream, only the Fermat kernel on the caller's.  A fake device records every launch with its stream, every event record and wait, and the host
    # reads (a synchronous read returns after everything its stream had before it: the host issues the next launches after that).
    ROUND = [("fr_plan", "ctl"), ("cumsum", "ctl"), ("fr_info", "ctl"), ("host_read", "ctl"), ("fr_expand", "ctl"), ("event", "ctl"),
             ("test", "cur"), ("event", "cur"), ("fr_post", "ctl"), ("cumsum", "ctl"), ("fr_compact", "ctl")]
    TAIL = [("fr_plan", "ctl"), ("cumsum", "ctl"), ("fr_info", "ctl"), ("host_read", "ctl"), ("event", "ctl")]

    def unordered(ops):
        """the (launch, previous launch) pairs where a launch does not happen after the launch issued before it (events skipped): the two streams' launches must be ONE chain, as on one stream"""
        reach, bad, prev = [], [], None
        for i, (name, st, preds) in enumerate(ops):
            m = 0
            for q in preds:
                m |= reach[q] | (1 << q)
            reach.append(m)
            if name != "event":
                if prev is not None and not (m >> prev) & 1:
                    bad.append((ops[prev][0] + "@" + ops[prev][1], name + "@" + st))
                prev = i
        return bad

    def run_ctl(fn):
        DEV.reset()
        ctl = FakeStream(DEV, "ctl")
        try:
            out, err = fn(ctl), None
        except RuntimeError as e:
            out, err = None, str(e)
        DEV.issue("after-return")                              # what the caller launches next on its stream
        return out, err, list(DEV.ops), len(DEV.stack)

    nchk = 0
    for p, n, mean_len, target, dmax in ((0.0715, 12000, 60, 1 << 20, 8), (0.0715, 3000, 300, 1 << 12, 8), (0.3, 2000, 20, 1 << 10, 3), (0.0, 400, 12, 1 << 12, 8), (1.0, 400, 12, 1 << 12, 8)):
        kv, cnt, cols = make_pool(rng, n, mean_len=mean_len)
        args.dmax, args.target = dmax, target
        a = ref(FakeTester(p), kv, cnt, cols)
        b = fround.run_pool_fused(FakeTester(p), kv, cnt, cols, target=target, dmax=dmax, check_range=True)
        out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(p), kv, cnt, cols, target=target, dmax=dmax, check_range=True, ctl_stream=ctl))
        first = next(i for i, o in enumerate(ops) if o[0] == "fr_plan")
        names = [(o[0], o[1]) for o in ops[first:-1]]
        pattern = (err is None and names == ROUND * out[5] + TAIL and (ops[first - 1][0], ops[first - 1][1]) == ("event", "cur") and ops[-1][:2] == ("after-return", "cur"))
        bad = unordered(ops)
        good = err is None and same(out, a) and same(out, b) and out[4] == a[4] and out[5] == a[5] and pattern and not bad and depth == 1
        print(f"  ctl_stream: p={p} n={n} lists ~{mean_len} target 2^{target.bit_length() - 1} dmax {dmax}: {out[5]} rounds, {len(ops)} launches on two streams, results identical to run_pool and to "
              f"the one-stream mode, launch order as expected, one chain: {'ok' if good else 'FAILED'}" + ("" if not bad else f"  unordered: {bad[:3]}"), flush=True)
        ok &= good
        nchk += 1
    # the checker has teeth: the same run with every wait_event ignored (the Fermat kernel and the bookkeeping could overlap) is caught
    kv, cnt, cols = make_pool(rng, 3000, mean_len=60)
    DEV.ignore_waits = True
    try:
        out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(0.0715), kv, cnt, cols, target=1 << 12, dmax=8, check_range=True, ctl_stream=ctl))
    finally:
        DEV.ignore_waits = False
    bad = unordered(ops)
    good = len(bad) > 0 and err is None
    print(f"  ctl_stream with the event waits left out: {len(bad)} launches not ordered after their predecessor (e.g. {bad[0] if bad else None}): {'caught' if good else 'NOT CAUGHT'}", flush=True)
    ok &= good
    # the two errors with ctl_stream: the same messages, the stream stack restored (a `with` left through the exception)
    kv, cnt, cols = make_pool(rng, 3000, mean_len=60, unsorted=3)
    args.kernel = 28
    out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(0.0715), kv, cnt, cols, target=1 << 12, dmax=8, check_range=True, ctl_stream=ctl))
    good = err == "a member's rows are not tested in ascending order" and depth == 1 and not unordered(ops)
    print(f"  ctl_stream, rows not ascending: {err!r}, current stream restored: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    kv, cnt, cols = make_pool(rng, 3000, mean_len=60)
    out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(0.0715, range_bad=0.001), kv, cnt, cols, target=1 << 12, dmax=8, check_range=True, ctl_stream=ctl))
    good = err == "kernel 28 flagged an n outside its range" and depth == 1 and not unordered(ops)
    print(f"  ctl_stream, a flag above 1 with kernel 28: {err!r}, current stream restored: {'ok' if good else 'FAILED'}", flush=True)
    ok &= good
    # half pools (what run_pool_split passes: a slice of the pool and target // 2) and the profile line
    sl = (kv[:1500], cnt[:1500], cols[:int(cnt[:1500].sum())])
    args.dmax, args.target = 8, 1 << 20
    r = ref(FakeTester(0.0715), *sl, target=(1 << 20) // 2)
    out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(0.0715), *sl, target=(1 << 20) // 2, dmax=8, check_range=True, ctl_stream=ctl))
    good = err is None and same(out, r) and not unordered(ops)
    print(f"  ctl_stream, a half of a pool (1500 members, target 2^19): {'identical' if good else 'DIFFERENT'}", flush=True)
    ok &= good
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out, err, ops, depth = run_ctl(lambda ctl: fround.run_pool_fused(FakeTester(0.0715), *sl, target=1 << 12, dmax=8, check_range=True, profile=True, ctl_stream=ctl))
    good = err is None and "[profile-pool] [fused rounds]" in buf.getvalue() and not unordered(ops)
    print(f"  ctl_stream with profile=True: the profile line is printed, order intact: {'ok' if good else 'FAILED'}", flush=True)
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

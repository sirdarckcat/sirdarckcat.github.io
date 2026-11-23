#!/usr/bin/env python3
"""campaign3 on a GPU, version 5: search_gpu3.py with its GPU sieve replaced by the uarch session's sieve200/cuda kernels (GpuFeeder:
one CTA per row with the window's bit map in shared memory, Barrett reduction, a bit-sliced counter, selection by histogram, and
the kept members' rows straight from the bit matrix). Everything runs on the GPU; the host CPUs stay free.

    python3 search_gpu5.py slices.json [--skip-frac F] [--kernel 28] [--klog 19] [--sieve200 DIR] ...
    python3 search_gpu5.py --campaign DIR [--batch 32] [--kmax ...] [--klo ...] [--desc] [--no-stop] ...

Selection, accounting and log lines are search_gpu3.py's:
- per block of 2^llog = --block members (2^15 = search.run_block's blocks), the emptiest ceil(L(1-f)) by survivor count, ties
  by ascending k (exactly np.argsort(counts, kind="stable")[:keep]);
- hit% from the hit masses sum (1 - p_est)^count;
- tests counted up to each member's first base-2 PRP.
check_v5.sh compares the slice lines with search_gpu3.py's on production slices. Slices must be whole windows of 2^klog members.
"""
import argparse, json, math, os, re, sys, threading, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("specs", nargs="?")
ap.add_argument("--campaign")
ap.add_argument("--batch", type=int, default=16, help="slices per pool (campaign mode)")
ap.add_argument("--kmax", type=int, default=450_000_000, help="campaign mode: slices below this k (the 199-digit ceiling also caps)")
ap.add_argument("--klo", type=int, default=0, help="campaign mode: slices from this k up")
ap.add_argument("--desc", action="store_true", help="campaign mode: highest slices first (larger N: lower E, more hits per k)")
ap.add_argument("--no-stop", action="store_true", help="campaign mode: keep going after a hit (more hits, larger best g)")
ap.add_argument("--slice", type=int, default=1 << 20)
ap.add_argument("--block", type=int, default=32768)
ap.add_argument("--sieve-b", type=int, default=1000000)
ap.add_argument("--skip-frac", type=float, default=0.0)
ap.add_argument("--p-est", type=float, default=0.055)
ap.add_argument("--out", default="found.jsonl")
ap.add_argument("--near-miss", type=int, default=int(os.environ.get("NEAR_MISS", "0")),
                help="report a tested member whose FIRST probable-prime row q (rows ascending, every earlier row composite) is >= this: "
                     "then g(N) = q whatever the design Q. Verified on the CPU (every prime below q composite, N - q prime) and written to "
                     "--out with near_miss = true. 0: off. It changes nothing about which members are tested or how")
ap.add_argument("--goldbach", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ap.add_argument("--target", type=int, default=1 << 20, help="most tests in one launch")
ap.add_argument("--dmax", type=int, default=8, help="most complements of one member in one launch")
ap.add_argument("--pool", type=int, default=1 << 19, help="members collected before the pool is tested")
ap.add_argument("--klog", type=int, default=19, help="members per GPU sieve window: 2^klog")
ap.add_argument("--sieve-threads", type=int, default=256, help="GpuFeeder threads per CTA (1024 is faster on sm_80/89)")
ap.add_argument("--deep", type=int, default=0, choices=(0, 1),
                help="1: the uarch session's batch-level sieve (sieve200/cuda/deep_feeder.py): windows of 2^klog members (use --klog 25 --slice 33554432), primes up to --sieve-b, "
                     "those above --deep-split through the bucketed large-prime stage; kernel launches and memory as DEEPSIEVE.md says")
ap.add_argument("--deep-split", type=int, default=1000000, help="--deep: primes above this go through the large-prime stage")
ap.add_argument("--deep-rg", type=int, default=16, help="--deep: rows a group of the large-prime stage")
ap.add_argument("--deep-max-rows", type=int, default=1100, help="--deep: rows of the bit matrix (the most rows of any variant)")
ap.add_argument("--deep-tile-threads", type=int, default=256, help="--deep: CTA size of the tile kernel (128 leaves registers for co-resident Fermat CTAs with --overlap)")
ap.add_argument("--deep-gen-threads", type=int, default=256, help="--deep: CTA size of the large-prime generate kernel")
ap.add_argument("--fermat-cta-sm", type=int, default=0,
                help="with --overlap: launch the Fermat kernel in chunks of this many CTAs an SM (e.g. 3 of the 5 that fit), leaving registers and shared memory free on every SM "
                     "for the sieve's CTAs to sit beside them; 0 = one launch a round, as before")
ap.add_argument("--profile-pool", type=int, default=0, choices=(0, 1),
                help="1: time the Fermat kernels of every round of every pool with CUDA events and print, per pool, the rounds, the kernels' GPU seconds, the wall seconds of run_pool and the gap "
                     "between them (the GPU idle between rounds: the host's syncs and cupy calls), and the wall of the whole flush; no change to the results")
ap.add_argument("--pool-threads", type=int, default=1, choices=(1, 2),
                help="2: a pool's members are tested as two halves in two threads, each on its own CUDA stream (run_pool_split): while one half's host code runs between its Fermat rounds (syncs, ~40 small "
                     "cupy launches) the other half's kernel keeps the GPU busy; the same per-member results as 1 (counted tests, PRP flags, successes, first-PRP rows)")
ap.add_argument("--pipeline", type=int, default=0, choices=(0, 1),
                help="1: ONE sieve thread for the whole campaign (sieve200/cuda/overlap.py Pipeline): it plans the next batch itself and sieves its windows on a high-priority stream while the Fermat rounds of "
                     "the previous pool run, across batch boundaries (with --overlap the sieve of a batch cannot start before the previous batch's Fermat has ended).  Either --flush-each-window 1 "
                     "(--pipeline-depth 1: window i + 1 is sieved under the Fermat of window i) or production's pool (--pool 2097152, one flush a batch) with --pipeline-depth 2 (the whole of batch n + 1 is sieved "
                     "under the one flush of batch n: no extra flush, no extra waste)")
ap.add_argument("--pipeline-depth", type=int, default=1, choices=(1, 2, 3, 4),
                help="--pipeline: how many sieved windows may wait for the consumer (2 = the windows of a batch with one flush a batch; the held pool plus this many windows are alive: a window is ~0.8 GB of u16 rows "
                     "while it waits, ~1.6 GB as int32 rows in the pool)")
ap.add_argument("--flush-each-window", type=int, default=0, choices=(0, 1),
                help="1: test the pool after every window (a deep window keeps ~1M members: with --pool 2097152 the pool is tested once a batch, after ALL its windows are sieved, so nothing can overlap "
                     "unless --pipeline-depth 2 lets the sieve thread run a whole batch ahead).  Costs ~0.19 s a batch of tail rounds and waste against one flush")
ap.add_argument("--trace-pipeline", type=int, default=0, choices=(0, 1),
                help="--pipeline: after every batch print the seconds the consumer waited for the sieve (sieve time NOT hidden), the seconds the sieve thread spent making windows and waiting for the consumer "
                     "(it is Fermat-bound when it waits), and the windows made")
ap.add_argument("--overlap", type=int, default=0, choices=(0, 1),
                help="1: the sieve of the next window runs in a second thread on its own high-priority CUDA stream (sieve200/cuda/overlap.py) while the Fermat rounds of the pool run")
ap.add_argument("--sieve200", default=os.environ.get("SIEVE200_DIR", "/content/gs/goldbach/sieve200"), help="the uarch session's goldbach/sieve200 (with cuda/)")
ap.add_argument("--kernel", type=int, default=int(os.environ.get("SEARCH_GPU3_KERNEL", "2")), choices=(2, 3, 28),
                help="2: gpu_fermat.py (proven in Lean); 3: gpu_fermat3.py (dedicated squaring, lazy reduction, n < 2^(32L-7)); "
                     "28: the uarch session's gpu_fermat28.py (24 x 28-bit limbs; n in [2^642, 2^668))")
ap.add_argument("--k28-step", default=os.environ.get("K28_STEP", "fermat28_step_s1.cuh"),
                help="kernel 28's step file: fermat28_step_s1.cuh or _s1r.cuh with --k28-asm 1 (sm_120), _s1rw.cuh or _s1w.cuh with --k28-asm 0 (sm_80/89)")
ap.add_argument("--k28-asm", type=int, default=int(os.environ.get("K28_ASM", "1")), choices=(0, 1), help="kernel 28: PTX mad.wide (1) or plain C (0)")
args = ap.parse_args()
sys.path.insert(0, args.goldbach)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search                      # noqa: E402  (init_spec, verify_success)
from gmpy2 import mpz              # noqa: E402
import cupy as cp                  # noqa: E402
import cupyx                       # noqa: E402
from gpu_fermat import kernel as kernel2, to_limbs   # noqa: E402
from gpu_fermat3 import kernel as kernel3      # noqa: E402
sys.path.insert(0, os.path.join(args.sieve200, "cuda"))
from gpu_sieve import GpuFeeder               # noqa: E402
if args.overlap or args.pipeline:
    from overlap import overlapped, Pipeline     # noqa: E402  (sieve200/cuda, uarch b344e85)
if args.kernel == 28:
    sys.path.insert(0, os.environ.get("FERMAT28_DIR", "/content/f28"))
    import gpu_fermat28                       # noqa: E402

_VAR = {}                           # variant -> (U, N0 mod s) on the GPU
_FD = {}                            # row count -> GpuFeeder (its bit buffer reused across variants)
_SH = {}


def load_specs(path):
    specs = json.load(open(path))
    for s in specs:
        for f in ("residual", "cover"):
            if isinstance(s.get(f), str):
                s[f] = json.loads(s[f])
    return specs


_DEEP = {}                          # --deep: the DeepSieve of the current M (one BatchFeeder, one bit matrix for every variant)


def feeder_for(spec):
    """The GpuFeeder for this spec's row count, pointed at this variant (its U and N0 mod s).  --deep: the one BatchFeeder of deep_feeder.py, retargeted."""
    if args.deep:
        from deep_feeder import deep_feeder_for                  # noqa: E402  (sieve200/cuda)
        return deep_feeder_for(_DEEP, spec, B=args.sieve_b, ks_log=args.klog, llog=int(math.log2(args.block)), f=args.skip_frac, p_est=args.p_est,
                               split=args.deep_split, rg=args.deep_rg, max_rows=args.deep_max_rows, nthreads=256, log=lambda m: print(m, flush=True),
                               **({k: v for k, v in (("gen_threads", args.deep_gen_threads), ("tile_threads", args.deep_tile_threads)) if v != 256}))   # older trees take neither
    key = (spec["name"].split("@")[0], spec["N0"])
    if key not in _VAR:
        search.init_spec(spec, args.sieve_b, args.block)       # S, M^-1 mod s cached per M; N0 mod s per call
        G = search.G
        assert int(G["S"].max()) < 2**32 and len(G["U"]) < 4096
        if _SH.get("M") != spec["M"]:
            _FD.clear()
            _SH.clear(); _SH["M"] = spec["M"]
            _SH["fd0"] = GpuFeeder.from_search_G(G, klog=args.klog, llog=int(math.log2(args.block)), f=args.skip_frac, p_est=args.p_est,
                                                 nthreads=args.sieve_threads)
        _VAR[key] = (cp.asarray(np.asarray(G["U"], dtype=np.uint32)), cp.asarray(np.asarray(G["n0m"], dtype=np.uint32)), len(G["U"]))
    U, N0M, nU = _VAR[key]
    fd = _FD.get(nU)
    if fd is None:
        fd = _FD[nU] = _SH["fd0"].with_variant(cp.asnumpy(N0M), cp.asnumpy(U))
    fd.U, fd.N0M = U, N0M
    return fd


_NSM = cp.cuda.Device().attributes["MultiProcessorCount"]
_CQ = {}                            # (N0, rows, limbs) -> the device array of N0 - q (the same variants come back in every batch; exact keys)


def _cq_rows(N0, residual, limbs):
    key = (N0, tuple(int(q) for q in residual), limbs)
    a = _CQ.get(key)
    if a is None:
        if len(_CQ) >= 512:
            _CQ.pop(next(iter(_CQ)))
        a = _CQ[key] = cp.asarray(np.stack([to_limbs(N0 - int(q), limbs) for q in residual]))
    return a


class MultiTester:
    """cq rows N0_v - q of every variant in the batch (shared M); test(idx, k) -> uint8 flags."""
    def __init__(self, specs, limbs=21):
        M = int(specs[0]["M"])
        assert all(int(s["M"]) == M for s in specs), "a pool needs one M"
        parts, self.off, qs, n = [], [], [], 0
        for s in specs:
            N0 = int(s["N0"])
            assert N0 > max(s["residual"]), "N0 - q must be positive"
            assert all(int(a) < int(b) for a, b in zip(s["residual"], s["residual"][1:])), "residual rows must be ascending"
            self.off.append(n)
            part = _cq_rows(N0, s["residual"], limbs)
            parts.append(part); n += int(part.shape[0])
            qs.extend(int(q) for q in s["residual"])
        self.cq = parts[0] if len(parts) == 1 else cp.concatenate(parts)
        self.qrow = cp.asarray(np.array(qs, dtype=np.int64))      # q of every global row (for the first-PRP row of a member)
        self.M = cp.asarray(to_limbs(M, limbs))
        if args.kernel == 3:                                   # lazy reduction needs 16n < 2^(32L)
            nmax = max(int(sp["N0"]) + (int(sp.get("kmax", 1 << 32)) - 1) * M for sp in specs)
            assert nmax < 1 << (32 * limbs - 7), f"kernel 3 needs n < 2^{32 * limbs - 7}"
        if args.kernel == 28:                                  # fermat28 returns flag 2 outside [2^642, 2^668)
            for sp in specs:
                lo = int(sp["N0"]) - max(int(q) for q in sp["residual"]) + int(sp.get("kstart", 0)) * M
                hi = int(sp["N0"]) + (int(sp.get("kmax", 1 << 32)) - 1) * M
                assert lo >= 1 << 642 and hi < 1 << 668, f"kernel 28 needs 2^642 <= n < 2^668 ({sp['name']})"
            self.k = gpu_fermat28.kernel(limbs, step_file=args.k28_step, asm_mad=bool(args.k28_asm))
        else:
            self.k = (kernel3 if args.kernel == 3 else kernel2)(limbs)

    def test(self, idx, kv, threads=128):
        T = int(idx.size)
        out = cp.empty(T, dtype=cp.uint8)
        if T:
            step = args.fermat_cta_sm * _NSM * threads if args.fermat_cta_sm else T          # chunks of fermat_cta_sm CTAs an SM: room on every SM for a sieve CTA
            for lo in range(0, T, step):
                hi = min(T, lo + step)
                self.k(((hi - lo + threads - 1) // threads,), (threads,), (self.cq, self.M, idx[lo:hi], kv[lo:hi], out[lo:hi], np.int32(hi - lo)))
        return out


def verify_near_miss(spec, k, q):
    """g(N) = q for N = N0 + k M?  Every prime p < q has N - p composite (is_prime: BPSW + Miller-Rabin; a False is definite)
    and N - q is a probable prime (the certifier proves it).  Returns the found.jsonl record or None."""
    from sympy import primerange                           # noqa: E402
    import gmpy2                                           # noqa: E402
    N = mpz(spec["N0"]) + k * mpz(spec["M"])
    if not gmpy2.is_prime(q) or not gmpy2.is_prime(N - q, 30):
        return None
    for p in primerange(2, q):
        if gmpy2.is_prime(N - p, 25):
            return None
    return {"k": k, "N": str(N), "digits": len(str(N)), "g": int(q), "near_miss": True, "Q": int(spec["Q"])}


def run_pool(tester, kv, cnt, cols, target=None):
    """Members kv[m] with survivors cols[indptr[m]:indptr[m+1]] (global cq rows, ascending q).
    Returns per member: tests counted up to the first PRP, whether a PRP was found, success, the global row of the first
    PRP (-1 if none); and the tests computed on the GPU.  Every row a member is tested on is checked, as it is tested, to be
    above the member's previous tested row (rows strictly ascending, so q ascending: the rows of a variant are its residual
    list, checked ascending in MultiTester), and a round's first PRP is the lowest offset with flag 1: the first-PRP row is
    the first probable prime over the member's fully tested prefix."""
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
        if prof is not None:
            e0 = cp.cuda.Event(); e1 = cp.cuda.Event(); e0.record()
        flags = tester.test(rowsv, kv[act][m_of].astype(cp.uint32))
        if prof is not None:
            e1.record(); prof.append((e0, e1, total))
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
    if prof is not None:
        cp.cuda.Device().synchronize()
        wall = time.perf_counter() - t_prof
        kern = sum(cp.cuda.get_elapsed_time(a, b) for a, b, _ in prof) / 1e3          # (cupy has no Event.elapsed_time: the module function)
        print(f"[profile-pool] {n} members, {launches} rounds, {gtests} tests: Fermat kernels {kern:.3f} s on the GPU, run_pool wall {wall:.3f} s, gap {wall - kern:.3f} s "
              f"({100 * (wall - kern) / max(wall, 1e-9):.1f}% of run_pool); {gtests / max(kern, 1e-9) / 1e6:.1f}M tests/s while a kernel runs, {gtests / max(wall, 1e-9) / 1e6:.1f}M over the pool", flush=True)
    return tests_m, prp_m, succ_m, frow, gtests, launches


_SPLIT_STREAMS = []             # two long-lived streams: cupy's pool keeps a free list per stream, so a stream made for every pool would strand its blocks


def run_pool_split(tester, kv, cnt, cols):
    """run_pool on two halves of the members (split at a member boundary) in two threads, each on its own non-blocking stream.  Same results per member as run_pool; the numbers of computed tests and launches
    differ a little (a half's rounds are sized by its own active members)."""
    n = int(kv.size)
    if n < 4096:
        return run_pool(tester, kv, cnt, cols)
    if not _SPLIT_STREAMS:
        _SPLIT_STREAMS.extend(cp.cuda.Stream(non_blocking=True) for _ in range(2))
    offs = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])          # (also waits for the caller's stream: kv, cnt and cols are complete before the threads read them)
    mid = n // 2
    cut, end = int(offs[mid]), int(offs[n])
    parts = [(0, mid, 0, cut), (mid, n, cut, end)]
    res, err = [None, None], []
    dev = cp.cuda.Device().id

    def work(i):
        try:
            cp.cuda.Device(dev).use()
            a, b, ca, cb = parts[i]
            with _SPLIT_STREAMS[i]:
                res[i] = run_pool(tester, kv[a:b], cnt[a:b], cols[ca:cb], target=args.target // 2)         # half the tests a round: the same rows a member per round (the same waste) as one pool
                _SPLIT_STREAMS[i].synchronize()
        except BaseException as e:                                          # handed to the caller
            err.append(e)
    ths = [threading.Thread(target=work, args=(i,)) for i in range(2)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    if err:
        raise err[0]
    (t0, p0, s0, f0, g0, l0), (t1, p1, s1, f1, g1, l1) = res
    out = (cp.concatenate([t0, t1]), cp.concatenate([p0, p1]), cp.concatenate([s0, s1]), cp.concatenate([f0, f1]), g0 + g1, l0 + l1)
    cp.cuda.get_current_stream().synchronize()                              # the concatenations are done before the halves' arrays go back to their streams' free lists
    return out


def batch_plan(batch, K):
    """(slice index, spec, kstart, kmax) of every slice of a batch, checked before any GPU work; the sieve thread (--pipeline) and run_batch use the same plan"""
    plan = []
    for si, spec in enumerate(batch):
        kstart, kmax = spec["kstart"], spec["kmax"]
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        assert kstart % K == 0 and (kmax - kstart) % K == 0, "slices must be whole GPU sieve windows"
        plan.append((si, spec, kstart, kmax))
    return plan


def sieve_windows(batch):
    """the sieve: (slice index, window) in order"""
    K = 1 << args.klog
    for si, spec, kstart, kmax in batch_plan(batch, K):
        fd = feeder_for(spec)
        for w0 in range(kstart, kmax, K):
            yield si, fd.window(w0)


def run_batch(batch, out, pipe=None):
    """Sieve, select and test the slices in batch as one pool. Returns (lines, found, stats).  pipe: the campaign's Pipeline (--pipeline 1): its windows instead of a sieve of our own."""
    t0 = time.time()
    tester = MultiTester(batch)
    L = args.block
    st = [dict(alive=0, hmk=0.0, hma=0.0, kdone=0, tests=0, prps=0, succ=[], near=[], kmax=0) for _ in batch]
    pool = []                                                    # (sid, kv, cnt, cols) chunks
    npool = [0]
    gt = [0, 0, 0.0]                                             # tests computed, launches, expected hits

    def flush():
        if not pool:
            return
        t_flush = time.perf_counter()
        sid = cp.concatenate([cp.full(int(c[1].size), c[0], cp.int32) for c in pool])
        kv = cp.concatenate([c[1] for c in pool])
        cnt = cp.concatenate([c[2] for c in pool])
        cols = pool[0][3] if len(pool) == 1 else cp.concatenate([c[3] for c in pool])      # (a deep window is a pool of its own: no 1.5 GB copy)
        if args.overlap or args.pipeline:
            cp.cuda.get_current_stream().synchronize()               # the concatenations are done before the pool entries go back to the sieve thread's allocator
        pool.clear(); npool[0] = 0
        tests_m, prp_m, succ_m, frow, g, nl = (run_pool_split if args.pool_threads > 1 else run_pool)(tester, kv, cnt, cols)
        gt[0] += g; gt[1] += nl
        tt, pp = int(tests_m.sum()), int(prp_m.sum())
        if tt:                                                   # expected successes of the tested members: sum (1 - p^)^count
            gt[2] += float(((1.0 - pp / tt) ** cnt.astype(cp.float64)).sum())
        for si in range(len(batch)):
            m = sid == si
            st[si]["tests"] += int(tests_m[m].sum())
            st[si]["prps"] += int(prp_m[m].sum())
            st[si]["succ"].extend(int(k) for k in kv[m & succ_m].tolist())
        if args.near_miss:                                       # first-PRP row >= the threshold: g(N) = that q
            qf = cp.where(frow >= 0, tester.qrow[cp.maximum(frow, 0)], -1)
            nm = cp.nonzero(qf >= args.near_miss)[0]
            for i, si, k, q in zip(nm.tolist(), sid[nm].tolist(), kv[nm].tolist(), qf[nm].tolist()):
                st[si]["near"].append((int(k), int(q)))
        if args.profile_pool:
            print(f"[profile-pool] flush wall {time.perf_counter() - t_flush:.3f} s (the pool's Fermat rounds, its concatenations and the per-slice statistics)", flush=True)

    K = 1 << args.klog
    plan = batch_plan(batch, K)                                  # (si, spec, kstart, kmax), checked before any GPU work
    for si, spec, kstart, kmax in plan:
        st[si]["kmax"] = kmax
    nwin = sum(len(range(kstart, kmax, K)) for _, _, kstart, kmax in plan)
    for si, w in (pipe.windows(nwin) if pipe else overlapped(cp, sieve_windows(batch)) if args.overlap else sieve_windows(batch)):
        st[si]["alive"] += int(w.alive_total.sum())
        st[si]["kdone"] += K
        st[si]["hmk"] += float(w.hm_kept.sum()); st[si]["hma"] += float(w.hm_all.sum())
        rows32 = w.rows.astype(cp.int32)
        rows32 += np.int32(tester.off[si])                       # in place: one int32 copy of the survivor rows, not two (uarch b344e85)
        pool.append((si, w.k.astype(cp.int64), w.cnt.astype(cp.int64), rows32))
        if args.overlap or args.pipeline:
            cp.cuda.get_current_stream().synchronize()           # the copies above are done before w's arrays go back to the sieve thread's allocator
        w.rows = None                                            # after the synchronize (uarch 5499787): the u16 rows go back to the pool only once read
        npool[0] += int(w.k.size)
        if npool[0] >= args.pool or args.flush_each_window:
            flush()
    flush()
    dt = (time.time() - t0) / len(batch)
    lines, found = [], []
    for si, spec in enumerate(batch):
        s = st[si]
        nf = 0
        for k in sorted(s["succ"]):
            res = search.verify_success(spec, int(k))
            if res:
                res["name"] = spec["name"]
                found.append(res); nf += 1
                lines.append(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} g={res['g']}")
                out.write(json.dumps(res) + "\n"); out.flush()
        for k, q in sorted(s["near"]):
            res = verify_near_miss(spec, int(k), int(q))
            if res:                                              # not counted in found= (that is design-Q successes)
                res["name"] = spec["name"]
                found.append(res)
                lines.append(f"  SUCCESS-NEARMISS {spec['name']} k={k} digits={res['digits']} g={res['g']} (first PRP row, design Q={spec['Q']})")
                out.write(json.dumps(res) + "\n"); out.flush()
            else:
                lines.append(f"  NEARMISS-REJECTED {spec['name']} k={k} q={q} (CPU check failed)")
        kd = max(s["kdone"], 1)
        phat = s["prps"] / s["tests"] if s["tests"] else 0.0
        e_hat = (s["alive"] / kd) * phat
        hshare = s["hmk"] / s["hma"] if s["hma"] else 1.0
        lines.append(f"[{spec['name']}] k=[{spec['kstart']},{s['kmax']}) {dt:.0f}s ({kd/dt:.0f} k/s) tests={s['tests']} "
                     f"prp={s['prps']} p^={phat:.4f} alive/k={s['alive']/kd:.1f} E^={e_hat:.2f} "
                     f"hit%={100*hshare:.1f} found={nf}")
    tests = sum(s["tests"] for s in st)
    stats = (f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} batch {batch[0]['name']}..{batch[-1]['name']} "
             f"({len(batch)} slices) {dt*len(batch):.1f}s: tests {tests} counted, {gt[0]} computed "
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches, expected hits {gt[2]:.4e}, found {len(found)} [v5 gpu-sieve]" + (f" [near-miss >= {args.near_miss}]" if args.near_miss else ""))
    return lines, found, stats


def campaign(D):
    specs = load_specs(os.path.join(D, "my_specs.json"))
    LOG, FOUND, STATS = (os.path.join(D, f) for f in ("search.log", "found.jsonl", "gpu3_stats.log"))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    out = open(FOUND, "a")

    def select_batch(excluded):                                  # the next `--batch` slices that are not in `excluded`
        batch = []
        top = (args.kmax - 1) // args.slice * args.slice
        k0s = range(top, args.klo - 1, -args.slice) if args.desc else range(args.klo // args.slice * args.slice, args.kmax, args.slice)
        for k0 in k0s:
            for s in specs:
                name = f"{s['name']}@{k0}"
                if name not in excluded:
                    batch.append(dict(s, name=name, kstart=k0, kmax=min(k0 + args.slice, args.kmax)))
                    if len(batch) >= args.batch:
                        break
            if len(batch) >= args.batch:
                break
        return batch

    planned = set(done)                                          # --pipeline: the sieve thread plans ahead of the batches that are finished

    def plan_next():
        b = select_batch(planned)
        planned.update(x["name"] for x in b)
        return b
    pipe = Pipeline(cp, plan_next, sieve_windows, depth=args.pipeline_depth) if args.pipeline else None
    while True:
        if not args.no_stop and os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
            print("C3GPU-HIT: found.jsonl is not empty", flush=True)
            return 3
        batch = pipe.next_batch() if pipe else select_batch(done)
        if not batch:
            print("C3GPU-EXHAUSTED", flush=True)
            return 2
        lines, found, stats = run_batch(batch, out, pipe)
        if pipe and args.trace_pipeline:
            ps = pipe.take_stats()
            print(f"[pipeline] batch {batch[0]['name']}..{batch[-1]['name']}: the consumer waited {ps['wait']:.3f} s for the sieve; the sieve thread made {ps['windows']} windows in {ps['busy']:.3f} s "
                  f"and waited {ps['idle']:.3f} s for the consumer ({time.strftime('%H:%M:%S', time.gmtime())}Z)", flush=True)
        with open(LOG, "a") as f:
            f.write("\n".join(lines) + "\n")
        with open(STATS, "a") as f:
            f.write(stats + "\n")
        done.update(b["name"] for b in batch)


def main():
    if args.campaign:
        sys.exit(campaign(args.campaign))
    specs = load_specs(args.specs)
    out = open(args.out, "a")
    for i in range(0, len(specs), args.batch):
        lines, found, stats = run_batch(specs[i:i + args.batch], out)
        print("\n".join(lines), flush=True)
        print("#", stats, flush=True)


if __name__ == "__main__":
    main()

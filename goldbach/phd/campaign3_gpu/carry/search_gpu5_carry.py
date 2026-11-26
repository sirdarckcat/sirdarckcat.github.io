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
import argparse, bisect, collections, glob, json, math, os, re, sys, threading, time
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
ap.add_argument("--record", type=int, default=int(os.environ.get("RECORD_G", "0")),
                help="the record g (the lead's calibration rule of 25 Nov 18:52Z): a verified near-miss with g <= RECORD is a sub-record event, written to near_events.jsonl "
                     "beside --out (each N once, \"sub_record\": true) instead of found.jsonl, which keeps the records (g > RECORD) and every design hit. 0: off")
ap.add_argument("--near-miss", type=int, default=int(os.environ.get("NEAR_MISS", "0")),
                help="report a tested member whose FIRST probable-prime row q (rows ascending, every earlier row composite) is >= this: "
                     "then g(N) = q whatever the design Q. Verified on the CPU (every prime below q composite, N - q prime) and written to "
                     "--out with near_miss = true. 0: off. It changes nothing about which members are tested or how")
ap.add_argument("--goldbach", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ap.add_argument("--target", type=int, default=1 << 20, help="most tests in one launch")
ap.add_argument("--dmax", type=int, default=8, help="most complements of one member in one launch")
ap.add_argument("--fused-rounds", type=int, default=0, choices=(0, 1),
                help="1: the bookkeeping of the Fermat rounds on the device (fermat661/cuda/fround.py + fround_kernels.cuh, next to gpu_fermat28.py in FERMAT28_DIR): ~10 launches and one host read a round "
                     "instead of ~100 small cupy kernels and ~6 syncs, the same test lists and per-member results as run_pool (--profile-pool prints the same line for them)")
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
ap.add_argument("--carry-over", type=int, default=0, choices=(0, 1),
                help="1 (campaign mode, --fused-rounds 1): a pool (each part of it with --pool-threads 2) stops at the first round that would start with fewer than --carry-stop active "
                     "members, and its undecided members go on in the next pool with the rows they have left (fround.run_pool_fused stop_below / carry_state, the uarch session's "
                     "g200k/costside): no tail of small rounds, and with the default stop no test past a first PRP.  A slice's line is printed, with its SUCCESS / NEARMISS lines in "
                     "run_batch's order, once every member of the slice is decided (a few batches later); its counted tests and expected hits / near-misses go into the stats line of "
                     "that batch; its found records are written as soon as they are verified, each N once (a record already in found.jsonl is not written again).  A restart redoes "
                     "the slices whose lines were not printed.  The per-member results, so the slice lines (but their s and k/s), are those of a run without it")
ap.add_argument("--carry-stop", type=int, default=0,
                help="--carry-over: a pool (a part) stops at the first round with fewer active members than this; 0: (its target) // 2 + 1, i.e. D = 1 in every round")
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
ap.add_argument("--vector-dir", default=None,
                help="campaign mode for SHORT vectors (e.g. covers on 89 moduli, ~2e7 members a vector): the specs come from DIR/vec_*.json chunk files (read in name order, more as they "
                     "appear), and every vector is ONE slice of 2^klog members from k_lo, the first k with --vector-digits digits (N0 + k M >= 10^(digits - 1)); a vector whose window "
                     "does not fit below its kmax is skipped.  --klo / --kmax / --slice / --desc are not used then")
ap.add_argument("--vector-digits", type=int, default=200, help="--vector-dir: the digits every N must have (the window starts at the first such k)")
ap.add_argument("--vector-place", default="bottom", choices=("bottom", "top"),
                help="--vector-dir: the window from the first k with --vector-digits digits (bottom) or ending at the last k with N below 10^digits (top: larger N, slightly lower prime density, ~+1.5%% hits a vector); a vector whose name is in the done set under either placement is not taken again")
ap.add_argument("--vector-wait", type=int, default=900, help="--vector-dir: seconds to wait for a new chunk file before the campaign ends as exhausted")
ap.add_argument("--log-near-exp", type=int, default=0, choices=(0, 1),
                help="1: also log, per batch, the expected number of tested members whose first probable-prime row is at or above --near-miss (design hits included): "
                     "sum (1 - p^)^c over the tested members, c = the member's sieved-alive rows below the threshold")
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
assert not args.carry_over or (args.fused_rounds and args.campaign), "--carry-over needs --fused-rounds 1 and --campaign"
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
        a = _CQ[key] = cp.asarray(cq_limbs(N0, residual, limbs))
    return a


def cq_limbs(N0, residual, limbs):
    """The rows of to_limbs(N0 - q, limbs) for every q (little-endian 32-bit limbs), vectorized: q < 2^32, so after the first limb only a borrow moves on
    (np.stack of one to_limbs per row took ~10 ms a vector of 1,250 rows: with a new vector every window, the host time of a batch)."""
    q = np.asarray([int(x) for x in residual], dtype=np.int64)
    assert q.size and int(q.min()) >= 0 and int(q.max()) < (1 << 32) and int(N0) > int(q.max())
    out = np.tile(np.asarray(to_limbs(int(N0), limbs), dtype=np.int64), (q.size, 1))
    borrow = q
    for j in range(limbs):
        d = out[:, j] - borrow
        borrow = (d < 0).astype(np.int64)
        out[:, j] = d + (borrow << 32)
        if not borrow.any():
            break
    assert not borrow.any()
    return out.astype(np.uint32)


_COUNT_BELOW = None


def count_below(cols, offs, sid, thr_row):
    """For every member m (its rows cols[offs[m]:offs[m+1]], ascending global rows of the variant sid[m]): how many rows lie below thr_row[sid[m]]
    (binary search; --log-near-exp)"""
    global _COUNT_BELOW
    if _COUNT_BELOW is None:
        _COUNT_BELOW = cp.RawKernel(r"""
extern "C" __global__ void count_below(const int *cols, const long long *offs, const int *sid, const int *thr, long long n, int *out) {
    long long m = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (m >= n) return;
    long long lo = offs[m], hi = offs[m + 1];
    const long long a = lo;
    const int t = thr[sid[m]];
    while (lo < hi) { long long mid = (lo + hi) >> 1; if (cols[mid] < t) lo = mid + 1; else hi = mid; }
    out[m] = (int)(lo - a);
}""", "count_below")
    n = int(sid.size)
    out = cp.empty(n, dtype=cp.int32)
    if n:
        _COUNT_BELOW(((n + 255) // 256,), (256,), (cols, offs, sid, thr_row, np.int64(n), out))
    return out


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
        if args.log_near_exp and args.near_miss:                 # the global row index below which a variant's rows are < --near-miss
            self.thr_row = cp.asarray(np.array([o + bisect.bisect_left([int(q) for q in s["residual"]], args.near_miss) for o, s in zip(self.off, specs)], dtype=np.int32))
        self.M = cp.asarray(to_limbs(M, limbs))
        if args.kernel == 3:                                   # lazy reduction needs 16n < 2^(32L)
            nmax = max(int(sp["N0"]) + (int(sp.get("kmax", 1 << 32)) - 1) * M for sp in specs)
            assert nmax < 1 << (32 * limbs - 7), f"kernel 3 needs n < 2^{32 * limbs - 7}"
        if args.kernel == 28:                                  # fermat28 returns flag 2 outside [2^642, 2^nmax): nmax 668 (24 x 28-bit steps), 665 (fermat29_step_*.cuh: 23 x 29 bits, R = 2^669)
            nmax = gpu_fermat28.step_nmax(args.k28_step)
            for sp in specs:
                lo = int(sp["N0"]) - max(int(q) for q in sp["residual"]) + int(sp.get("kstart", 0)) * M
                hi = int(sp["N0"]) + (int(sp.get("kmax", 1 << 32)) - 1) * M
                assert lo >= 1 << 642 and hi < 1 << nmax, f"kernel 28 with {args.k28_step} needs 2^642 <= n < 2^{nmax} ({sp['name']})"
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


def true_g(N):
    """g(N) from N alone: the least prime p with N - p a probable prime (gmpy2.is_prime, 25 rounds; a False is definite).  Only for a
    CPU re-check that failed (the lead's rule of 25 Nov 10:20Z): the GPU's claim is then replaced by the CPU's value."""
    import gmpy2                                           # noqa: E402
    N = mpz(N)
    p = mpz(2)
    while not gmpy2.is_prime(N - p, 25):
        p = gmpy2.next_prime(p)
    return int(p)


def kernel_discrepancy(spec, k, claimed_q, out, lines):
    """A CPU re-check of a GPU claim failed (claimed_q: the member's claimed first-PRP row; None: a claimed design hit).  Never silent:
    g(N) is recomputed from N alone, logged loudly (C3GPU-KERNEL-DISCREPANCY on stdout, i.e. the driver log, in the search log, and in
    kernel_discrepancy.jsonl next to --out), and returned as a found.jsonl record when it is at or above --near-miss (Q without it)."""
    N = mpz(spec["N0"]) + k * mpz(spec["M"])
    g = true_g(N)
    Q = int(spec["Q"])
    claim = f"first PRP row q={claimed_q}" if claimed_q is not None else f"a design hit (no PRP row below Q={Q})"
    msg = f"C3GPU-KERNEL-DISCREPANCY {spec['name']} k={k}: the GPU claimed {claim}, the CPU re-check failed; g(N) from N alone = {g}"
    print(msg, flush=True)
    lines.append(f"  {msg} (re-check Error)")
    rec = {"k": int(k), "N": str(N), "digits": len(str(N)), "g": g, "near_miss": g < Q, "Q": Q, "name": spec["name"],
           "kernel_discrepancy": True, "claimed_q": claimed_q}
    with open(os.path.join(os.path.dirname(os.path.abspath(out.name)), "kernel_discrepancy.jsonl"), "a") as fh:
        fh.write(json.dumps(dict(rec, time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))) + "\n")
    return rec if g >= (args.near_miss or Q) else None


def record_discrepancy(spec, k, claimed_q, out, lines, found):
    """kernel_discrepancy, and the record written like any other found line when g reaches the threshold.  Returns 1 for a design hit."""
    res = kernel_discrepancy(spec, k, claimed_q, out, lines)
    if not res:
        return 0
    found.append(res)
    kind = "SUCCESS-NEARMISS" if res["near_miss"] else "SUCCESS"
    lines.append(f"  {kind} {spec['name']} k={k} digits={res['digits']} g={res['g']} (g(N) from N on the CPU after a kernel discrepancy, design Q={spec['Q']})")
    out.write(json.dumps(res) + "\n"); out.flush()
    return 0 if res["near_miss"] else 1


def run_pool(tester, kv, cnt, cols, target=None):
    """Members kv[m] with survivors cols[indptr[m]:indptr[m+1]] (global cq rows, ascending q).
    Returns per member: tests counted up to the first PRP, whether a PRP was found, success, the global row of the first
    PRP (-1 if none); and the tests computed on the GPU.  Every row a member is tested on is checked, as it is tested, to be
    above the member's previous tested row (rows strictly ascending, so q ascending: the rows of a variant are its residual
    list, checked ascending in MultiTester), and a round's first PRP is the lowest offset with flag 1: the first-PRP row is
    the first probable prime over the member's fully tested prefix."""
    if args.fused_rounds:
        import fround                                           # noqa: E402  (FERMAT28_DIR: next to gpu_fermat28.py)
        return fround.run_pool_fused(tester, kv, cnt, cols, target=args.target if target is None else target, dmax=args.dmax, check_range=(args.kernel == 28), profile=bool(args.profile_pool))
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


def _fermat_stream():
    """FERMAT_STREAM_PRIORITY=high: the Fermat halves' streams get the highest stream priority (with OVERLAP_SIEVE_PRIORITY=0 the sieve thread's stream is then below them: the sieve only gets what the Fermat
    CTAs leave free, which needs sieve CTAs that fit in the leftover registers: DEEP_TILE_MAXREG=32 with --deep-tile-threads 128 --deep-gen-threads 128).  Default: a plain non-blocking stream as before."""
    if os.environ.get("FERMAT_STREAM_PRIORITY", "") == "high":
        from overlap import new_stream                      # noqa: E402  (sieve200/cuda)
        return new_stream(cp, -100, "Fermat")
    return cp.cuda.Stream(non_blocking=True)


def run_pool_split(tester, kv, cnt, cols):
    """run_pool on two halves of the members (split at a member boundary) in two threads, each on its own non-blocking stream.  Same results per member as run_pool; the numbers of computed tests and launches
    differ a little (a half's rounds are sized by its own active members)."""
    n = int(kv.size)
    if n < 4096:
        return run_pool(tester, kv, cnt, cols)
    if not _SPLIT_STREAMS:
        _SPLIT_STREAMS.extend(_fermat_stream() for _ in range(2))
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


_CT = {}                            # --carry-over: slice name -> (its cq rows on the device, the q of its rows, its first row at or above --near-miss): made once, when the slice is new
_CT_KM = []                         # (the Fermat kernel, M) of the last CarryTester built with new slices (a drain has none)


class CarryTester(MultiTester):
    """--carry-over: MultiTester over every open slice (old_specs: the slices with members carried from the last pool; new_specs: the batch's).  The new slices are checked and their rows
    made by MultiTester itself, exactly as run_batch does; the older slices' tables are taken from _CT.  test() is MultiTester's."""
    def __init__(self, old_specs, new_specs, limbs=21):
        if new_specs:
            mt = MultiTester(new_specs, limbs)
            ends = mt.off[1:] + [int(mt.cq.shape[0])]
            qrow = cp.asnumpy(mt.qrow)
            thr = cp.asnumpy(mt.thr_row) if hasattr(mt, "thr_row") else None
            for i, (s, a, b) in enumerate(zip(new_specs, mt.off, ends)):
                _CT[s["name"]] = (mt.cq[a:b], qrow[a:b], int(thr[i]) - a if thr is not None else 0)
            _CT_KM[:] = [mt.k, mt.M]
        self.k, self.M = _CT_KM
        parts, self.off, qs, thr, n = [], [], [], [], 0
        for s in old_specs + new_specs:
            part, q, t = _CT[s["name"]]
            self.off.append(n); parts.append(part); qs.append(q); thr.append(n + t)
            n += int(part.shape[0])
        self.cq = parts[0] if len(parts) == 1 else cp.concatenate(parts)
        self.qrow = cp.asarray(np.concatenate(qs).astype(np.int64))
        if args.log_near_exp and args.near_miss:
            self.thr_row = cp.asarray(np.array(thr, dtype=np.int32))


class SliceState:
    """--carry-over: a slice whose line is not printed yet"""
    def __init__(self, uid, spec):
        self.uid, self.spec = uid, spec
        self.st = dict(alive=0, hmk=0.0, hma=0.0, kdone=0, tests=0, prps=0, succ=[], near=[], kmax=0)     # run_batch's per-slice statistics (succ / near: decided, not yet verified)
        self.windows_left = 0                                    # windows of the slice not yet in a pool
        self.outstanding = 0                                     # its members in a pool (or carried) and not decided
        self.ehits = self.enear = 0.0                            # expected hits / near-misses of its members, at the p^ of the pool each entered (run_batch's sums)
        self.groups = {}                                         # (0, k) / (1, k, q) -> the lines of a verified success / near-miss: printed before the slice line, in run_batch's order
        self.nf = 0                                              # design hits (found= of the slice line)
        self.dt = 0.0                                            # its batch's seconds a slice


class DedupOut:
    """found.jsonl with --carry-over: a record whose N is already in the file (written before a restart that redoes its slice) is not written again; .written counts the new ones"""
    def __init__(self, f, seen):
        self.f, self.seen, self.name, self.written = f, seen, f.name, 0

    def write(self, s):
        N = json.loads(s)["N"]
        if N in self.seen:
            return
        self.seen.add(N)
        self.written += 1
        self.f.write(s)

    def flush(self):
        self.f.flush()


class SplitOut:
    """--record R (the lead's calibration rule of 25 Nov 18:52Z): found.jsonl keeps the records (a near-miss with g > R) and every design hit; a near-miss with --near-miss <= g <= R is a
    sub-record event, written to near_events.jsonl beside it with "sub_record": true (each N once, also across a restart), so the tally can count the events against the logged expectation
    at --near-miss.  Records and their certification path are unchanged.  Has the file interface the writers use (name, write, flush)."""
    def __init__(self, found_path, near_path, record):
        self.f, self.name, self.record = open(found_path, "a"), found_path, int(record)
        self.near_seen = set()
        if os.path.exists(near_path):
            for l in open(near_path):
                try:
                    self.near_seen.add(json.loads(l)["N"])
                except (ValueError, KeyError, TypeError):
                    pass
        self.nf = open(near_path, "a")

    def write(self, s):
        try:
            r = json.loads(s)
        except ValueError:
            self.f.write(s)
            return
        if r.get("near_miss") and int(r.get("g", 0)) <= self.record:
            if r.get("N") in self.near_seen:
                return
            self.near_seen.add(r.get("N"))
            r["sub_record"] = True
            self.nf.write(json.dumps(r) + "\n")
            self.nf.flush()
            return
        self.f.write(s)

    def flush(self):
        self.f.flush()
        self.nf.flush()


class Carry:
    """--carry-over: the open slices (lines not printed; uid order) and, for every part of the pool (run_pool_split's halves), its undecided members: k, the rows they have left (as rows of
    their own slice's list: the tester's global rows change with the batch), their slice's uid, the tests counted so far"""
    def __init__(self, nparts, found_path):
        self.open, self.uid, self.parts, self.seen = [], 0, [None] * nparts, set()
        if os.path.exists(found_path):
            for l in open(found_path):
                try:
                    self.seen.add(json.loads(l)["N"])
                except (ValueError, KeyError, TypeError):
                    pass

    def members(self):
        return sum(int(p["kv"].size) for p in self.parts if p is not None)

    def rows(self):
        return sum(int(p["cols"].size) for p in self.parts if p is not None)


def _expand(lens, vals):
    """vals[m] repeated lens[m] times (lens int64 >= 1)"""
    total = int(lens.sum()) if int(lens.size) else 0
    if total == 0:
        return cp.zeros(0, vals.dtype)
    seg = cp.searchsorted(cp.cumsum(lens), cp.arange(total), side="right")
    return vals[seg]


def run_batch_carry(batch, out, pipe, carry, final=False):
    """run_batch with --carry-over: the batch's slices join the open ones; a pool is the batch's kept members plus the members carried from the last pool, and stops at --carry-stop
    (final: runs to its end).  Returns (lines, found records written, stats) like run_batch; the lines are those of the slices completed in this batch, in the order the slices were made."""
    import fround                                               # noqa: E402  (FERMAT28_DIR: next to gpu_fermat28.py; with stop_below / carry_state / carry_rows)
    t0 = time.time()
    new = []
    for spec in batch:
        new.append(SliceState(carry.uid, spec))
        carry.uid += 1
    old = list(carry.open)
    carry.open.extend(new)
    slices = old + new                                          # the tester's variants, uid ascending
    if not slices:
        return [], [], f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} batch (carry-over: nothing open)"
    slot = {s.uid: i for i, s in enumerate(slices)}
    tester = CarryTester([s.spec for s in old], [s.spec for s in new])
    off_g = cp.asarray(np.array(tester.off, dtype=np.int32))
    uid_g = cp.asarray(np.array([s.uid for s in slices], dtype=np.int64))
    uid0 = slices[0].uid
    lut_h = np.full(carry.uid - uid0, -1, dtype=np.int32)
    for s in slices:
        lut_h[s.uid - uid0] = slot[s.uid]
    lut = cp.asarray(lut_h)                                     # uid - uid0 -> the slice's variant in this tester
    P = args.pool_threads
    tgt = args.target // P                                      # run_pool_split's halves: half the target each
    S = args.carry_stop or tgt // 2 + 1
    nsl = len(slices)
    dout = DedupOut(out, carry.seen)
    gt = [0, 0]                                                 # tests computed, launches (this batch's pools)
    pool, npool = [], [0]

    def flush(fin):
        if not pool and carry.members() == 0:
            return
        if pool:                                                # the new members, as run_batch's flush
            sid = cp.concatenate([cp.full(int(c[1].size), c[0], cp.int32) for c in pool])
            kv = cp.concatenate([c[1] for c in pool])
            cnt = cp.concatenate([c[2] for c in pool])
            cols = pool[0][3] if len(pool) == 1 else cp.concatenate([c[3] for c in pool])
            if args.overlap or args.pipeline:
                cp.cuda.get_current_stream().synchronize()
        else:
            sid, kv, cnt, cols = cp.zeros(0, cp.int32), cp.zeros(0, cp.int64), cp.zeros(0, cp.int64), cp.zeros(0, cp.int32)
        pool.clear(); npool[0] = 0
        n = int(kv.size)
        if n:
            nper = cp.asnumpy(cp.bincount(sid, minlength=nsl))
            for i, s in enumerate(slices):
                s.outstanding += int(nper[i])
        offs = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
        cuts = [n * h // P for h in range(P + 1)]               # (P = 2: run_pool_split's mid = n // 2)
        parts = []
        for h in range(P):
            a, b = cuts[h], cuts[h + 1]
            ca, cb = int(offs[a]), int(offs[b])
            c = carry.parts[h]
            if c is not None:                                   # the carried members first, their rows moved to this tester's variants
                sl_c = lut[c["uid"] - uid0]
                colsg = c["cols"] + _expand(c["cnt"], off_g[sl_c])
                parts.append(dict(kv=cp.concatenate([c["kv"], kv[a:b]]), cnt=cp.concatenate([c["cnt"], cnt[a:b]]), cols=cp.concatenate([colsg, cols[ca:cb]]).astype(cp.int32),
                                  sl=cp.concatenate([sl_c, sid[a:b]]), prev=cp.concatenate([c["tests"], cp.zeros(b - a, cp.int64)])))
            else:
                parts.append(dict(kv=kv[a:b], cnt=cnt[a:b], cols=cols[ca:cb], sl=sid[a:b], prev=cp.zeros(b - a, cp.int64)))
        cp.cuda.get_current_stream().synchronize()              # the parts are complete before the threads read them on their own streams
        stop = 0 if fin else S
        res, err = [None] * P, []

        def run(h):
            pt = parts[h]
            return fround.run_pool_fused(tester, pt["kv"], pt["cnt"], pt["cols"], target=tgt, dmax=args.dmax, check_range=(args.kernel == 28), profile=bool(args.profile_pool),
                                         stop_below=stop, carry_state=True)
        if P == 1:
            res[0] = run(0)
        else:
            if not _SPLIT_STREAMS:
                _SPLIT_STREAMS.extend(_fermat_stream() for _ in range(2))
            dev = cp.cuda.Device().id

            def work(h):
                try:
                    cp.cuda.Device(dev).use()
                    with _SPLIT_STREAMS[h]:
                        res[h] = run(h)
                        _SPLIT_STREAMS[h].synchronize()
                except BaseException as e:                      # handed to the caller
                    err.append(e)
            ths = [threading.Thread(target=work, args=(h,)) for h in range(P)]
            for t in ths:
                t.start()
            for t in ths:
                t.join()
            if err:
                raise err[0]
        tt = pp = 0
        for r in res:
            gt[0] += r[4]; gt[1] += r[5]
            tt += int(r[0].sum()); pp += int(r[1].sum())
        if n and tt:                                            # the new members' expected hits (and near-misses) at this pool's p^, as run_batch's flush
            eh = cp.asnumpy(cp.bincount(sid, weights=(1.0 - pp / tt) ** cnt.astype(cp.float64), minlength=nsl))
            for i, s in enumerate(slices):
                s.ehits += float(eh[i])
            if args.log_near_exp and args.near_miss:
                cbl = count_below(cols, offs, sid, tester.thr_row)
                en = cp.asnumpy(cp.bincount(sid, weights=(1.0 - pp / tt) ** cbl.astype(cp.float64), minlength=nsl))
                for i, s in enumerate(slices):
                    s.enear += float(en[i])
        for h in range(P):
            pt = parts[h]
            tests_m, prp_m, succ_m, frow, _, _, unf, pos, _ = res[h]
            done = cp.ones(int(pt["kv"].size), cp.bool_)
            if int(unf.size):
                done[unf] = False
            sl, tot = pt["sl"], pt["prev"] + tests_m
            nd = cp.asnumpy(cp.bincount(sl[done], minlength=nsl))
            td = cp.asnumpy(cp.bincount(sl[done], weights=tot[done].astype(cp.float64), minlength=nsl))       # (integers below 2^53: exact)
            npr = cp.asnumpy(cp.bincount(sl[prp_m], minlength=nsl))
            for i, s in enumerate(slices):
                s.outstanding -= int(nd[i])
                s.st["tests"] += int(round(float(td[i])))
                s.st["prps"] += int(npr[i])
            ms = cp.nonzero(succ_m)[0]
            for i, k in zip(sl[ms].tolist(), pt["kv"][ms].tolist()):
                slices[i].st["succ"].append(int(k))
            if args.near_miss:                                  # first-PRP row >= the threshold: g(N) = that q
                qf = cp.where(frow >= 0, tester.qrow[cp.maximum(frow, 0)], -1)
                nm = cp.nonzero(qf >= args.near_miss)[0]
                for i, k, q in zip(sl[nm].tolist(), pt["kv"][nm].tolist(), qf[nm].tolist()):
                    slices[i].st["near"].append((int(k), int(q)))
            if int(unf.size):                                   # the undecided go on in the next pool: their rows left, as rows of their own slice
                lens, cols_u = fround.carry_rows(pt["cnt"], pt["cols"], unf, pos)
                sl_u = sl[unf]
                carry.parts[h] = dict(kv=pt["kv"][unf], cnt=lens, cols=(cols_u - _expand(lens, off_g[sl_u])).astype(cp.int32), uid=uid_g[sl_u], tests=tot[unf])
            else:
                carry.parts[h] = None
        cp.cuda.get_current_stream().synchronize()              # (as run_pool_split: done before the parts' arrays go back to their streams' free lists)

    K = 1 << args.klog
    plan = batch_plan(batch, K) if batch else []
    for si, spec, kstart, kmax in plan:
        new[si].st["kmax"] = kmax
        new[si].windows_left = len(range(kstart, kmax, K))
    nwin = sum(s.windows_left for s in new)
    if nwin:
        for si, w in (pipe.windows(nwin) if pipe else overlapped(cp, sieve_windows(batch)) if args.overlap else sieve_windows(batch)):
            s = new[si]
            s.st["alive"] += int(w.alive_total.sum())
            s.st["kdone"] += K
            s.st["hmk"] += float(w.hm_kept.sum()); s.st["hma"] += float(w.hm_all.sum())
            rows32 = w.rows.astype(cp.int32)
            rows32 += np.int32(tester.off[slot[s.uid]])
            pool.append((slot[s.uid], w.k.astype(cp.int64), w.cnt.astype(cp.int64), rows32))
            if args.overlap or args.pipeline:
                cp.cuda.get_current_stream().synchronize()
            w.rows = None
            npool[0] += int(w.k.size)
            s.windows_left -= 1
            if npool[0] >= args.pool or args.flush_each_window:
                flush(False)
    flush(final)
    dt = (time.time() - t0) / max(len(batch), 1)
    for s in new:
        s.dt = dt
    for s in slices:                                            # verify what was decided in this batch's pools: found records written now (run_batch's order within a slice)
        spec = s.spec
        for k in sorted(s.st["succ"]):
            gl = []
            res = search.verify_success(spec, int(k))
            if res:
                res["name"] = spec["name"]
                s.nf += 1
                gl.append(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} g={res['g']}")
                dout.write(json.dumps(res) + "\n"); dout.flush()
            else:                                               # the CPU found a PRP row below Q: recompute g(N), never drop it silently
                s.nf += record_discrepancy(spec, int(k), None, dout, gl, [])
            s.groups[(0, int(k))] = gl
        s.st["succ"] = []
        for k, q in sorted(s.st["near"]):
            gl = []
            res = verify_near_miss(spec, int(k), int(q))
            if res:                                             # not counted in found= (that is design-Q successes)
                res["name"] = spec["name"]
                gl.append(f"  SUCCESS-NEARMISS {spec['name']} k={k} digits={res['digits']} g={res['g']} (first PRP row, design Q={spec['Q']})")
                dout.write(json.dumps(res) + "\n"); dout.flush()
            else:
                gl.append(f"  NEARMISS-REJECTED {spec['name']} k={k} q={q} (CPU check failed)")
                s.nf += record_discrepancy(spec, int(k), int(q), dout, gl, [])
            s.groups[(1, int(k), int(q))] = gl
        s.st["near"] = []
    lines, printed = [], []
    for s in slices:                                            # the slices every member of which is decided: their lines, as run_batch's
        if s.windows_left or s.outstanding:
            continue
        printed.append(s)
        spec, st_ = s.spec, s.st
        for key in sorted(s.groups):
            lines.extend(s.groups[key])
        kd = max(st_["kdone"], 1)
        dts = max(s.dt, 1e-9)
        phat = st_["prps"] / st_["tests"] if st_["tests"] else 0.0
        e_hat = (st_["alive"] / kd) * phat
        hshare = st_["hmk"] / st_["hma"] if st_["hma"] else 1.0
        lines.append(f"[{spec['name']}] k=[{spec['kstart']},{st_['kmax']}) {s.dt:.0f}s ({kd/dts:.0f} k/s) tests={st_['tests']} "
                     f"prp={st_['prps']} p^={phat:.4f} alive/k={st_['alive']/kd:.1f} E^={e_hat:.2f} "
                     f"hit%={100*hshare:.1f} found={s.nf}")
        _CT.pop(spec["name"], None)
    done_uids = {s.uid for s in printed}
    carry.open = [s for s in carry.open if s.uid not in done_uids]
    assert not final or not carry.open, "a final pool left slices open"
    tests = sum(s.st["tests"] for s in printed)
    eh = sum(s.ehits for s in printed)
    en = sum(s.enear for s in printed)
    head = f"batch {batch[0]['name']}..{batch[-1]['name']}" if batch else "batch (carry-over drain)"
    stats = (f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {head} "
             f"({len(batch)} slices) {dt*len(batch):.1f}s: tests {tests} counted, {gt[0]} computed "
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches, expected hits {eh:.4e}, "
             + (f"expected near>={args.near_miss} {en:.4e}, " if args.log_near_exp and args.near_miss else "")
             + f"found {dout.written} [v5 gpu-sieve]" + (f" [near-miss >= {args.near_miss}]" if args.near_miss else "")
             + f" [carry-over: {len(printed)} slice lines; {carry.members()} members / {carry.rows()} rows into the next pool; {len(carry.open)} slices open]")
    return lines, [], stats


def batch_plan(batch, K):
    """(slice index, spec, kstart, kmax) of every slice of a batch, checked before any GPU work; the sieve thread (--pipeline) and run_batch use the same plan"""
    plan = []
    for si, spec in enumerate(batch):
        kstart, kmax = spec["kstart"], spec["kmax"]
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        assert (kmax - kstart) % K == 0 and (args.vector_dir or kstart % K == 0), "slices must be whole GPU sieve windows"
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
    gt = [0, 0, 0.0, 0.0]                                        # tests computed, launches, expected hits, expected first-PRP rows >= --near-miss (--log-near-exp)

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
            if args.log_near_exp and args.near_miss:             # ... and of the members whose first PRP row is >= --near-miss: the alive rows below it are all composite
                offs = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
                cb = count_below(cols, offs, sid, tester.thr_row)
                gt[3] += float(((1.0 - pp / tt) ** cb.astype(cp.float64)).sum())
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
            else:                                                # the CPU found a PRP row below Q: recompute g(N), never drop it silently
                nf += record_discrepancy(spec, int(k), None, out, lines, found)
        for k, q in sorted(s["near"]):
            res = verify_near_miss(spec, int(k), int(q))
            if res:                                              # not counted in found= (that is design-Q successes)
                res["name"] = spec["name"]
                found.append(res)
                lines.append(f"  SUCCESS-NEARMISS {spec['name']} k={k} digits={res['digits']} g={res['g']} (first PRP row, design Q={spec['Q']})")
                out.write(json.dumps(res) + "\n"); out.flush()
            else:
                lines.append(f"  NEARMISS-REJECTED {spec['name']} k={k} q={q} (CPU check failed)")
                nf += record_discrepancy(spec, int(k), int(q), out, lines, found)
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
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches, expected hits {gt[2]:.4e}, "
             + (f"expected near>={args.near_miss} {gt[3]:.4e}, " if args.log_near_exp and args.near_miss else "")
             + f"found {len(found)} [v5 gpu-sieve]" + (f" [near-miss >= {args.near_miss}]" if args.near_miss else ""))
    return lines, found, stats


class VectorSource:
    """--vector-dir: one slice per short vector, [k_lo, k_lo + K) with k_lo the first k at which N0 + k M has --vector-digits digits, from the chunk files
    DIR/vec_*.json read in name order as they appear (a producer on the host writes them ahead of the campaign; one chunk is held in memory)"""
    def __init__(self, D, K, digits, wait, place="bottom"):
        self.D, self.K, self.wait, self.place = D, K, wait, place
        self.lo, self.hi = mpz(10) ** (digits - 1), mpz(10) ** digits
        self.seen, self.queue, self.skipped = set(), collections.deque(), 0

    def _load_next(self, excluded):
        for f in sorted(glob.glob(os.path.join(self.D, "vec_*.json"))):
            if f in self.seen:
                continue
            self.seen.add(f)
            bases = {x.split("@")[0] for x in excluded}          # a vector scanned under either placement is done (the windows of one vector overlap)
            for s in load_specs(f):
                N0, M = mpz(s["N0"]), mpz(s["M"])
                k_lo = int((self.lo - N0 + M - 1) // M) if self.lo > N0 else 0
                kend = min(int(s["kmax"]), int((self.hi - 1 - N0) // M) + 1)   # first k with N >= 10^digits, or the spec's kmax
                kstart = k_lo if self.place == "bottom" else kend - self.K
                if kstart < k_lo or kstart + self.K > kend:     # the window must lie in the vector's range (N with --vector-digits digits)
                    self.skipped += 1
                    continue
                assert N0 + kstart * M >= self.lo and N0 + (kstart + self.K - 1) * M < self.hi, f"vector window outside [10^(d-1), 10^d): {s['name']}"
                name = f"{s['name']}@{kstart}"
                if name not in excluded and s["name"] not in bases:
                    self.queue.append(dict(s, name=name, kstart=kstart, kmax=kstart + self.K))
            return True
        return False

    def take(self, n, excluded):
        """the next n slices not in excluded; fewer if no new chunk is there (a short batch rather than a wait); [] after --vector-wait s without any"""
        out, t_end = [], time.time() + self.wait
        while len(out) < n:
            while self.queue and len(out) < n:
                x = self.queue.popleft()
                if x["name"] not in excluded:
                    out.append(x)
            if len(out) >= n or self._load_next(excluded):
                continue
            if out or time.time() > t_end:
                break
            time.sleep(5)
        return out


def campaign(D):
    specs = load_specs(os.path.join(D, "my_specs.json")) if not args.vector_dir else []
    src = VectorSource(args.vector_dir, 1 << args.klog, args.vector_digits, args.vector_wait, args.vector_place) if args.vector_dir else None
    LOG, FOUND, STATS = (os.path.join(D, f) for f in ("search.log", "found.jsonl", "gpu3_stats.log"))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    rec_g = int(getattr(args, "record", 0) or 0)
    out = SplitOut(FOUND, os.path.join(D, "near_events.jsonl"), rec_g) if rec_g else open(FOUND, "a")   # --record: sub-record near-misses to near_events.jsonl
    carry = Carry(args.pool_threads, FOUND) if args.carry_over else None

    def select_batch(excluded):                                  # the next `--batch` slices that are not in `excluded`
        if src:
            return src.take(args.batch, excluded)
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
            if carry is not None and carry.open:                 # --carry-over: the members still undecided, to their end; the last slice lines
                lines, found, stats = run_batch_carry([], out, None, carry, final=True)
                if lines:
                    with open(LOG, "a") as f:
                        f.write("\n".join(lines) + "\n")
                with open(STATS, "a") as f:
                    f.write(stats + "\n")
            print("C3GPU-EXHAUSTED", flush=True)
            return 2
        lines, found, stats = run_batch_carry(batch, out, pipe, carry) if carry is not None else run_batch(batch, out, pipe)
        if pipe and args.trace_pipeline:
            ps = pipe.take_stats()
            print(f"[pipeline] batch {batch[0]['name']}..{batch[-1]['name']}: the consumer waited {ps['wait']:.3f} s for the sieve; the sieve thread made {ps['windows']} windows in {ps['busy']:.3f} s "
                  f"and waited {ps['idle']:.3f} s for the consumer ({time.strftime('%H:%M:%S', time.gmtime())}Z)", flush=True)
        if lines:                                                # (--carry-over: a batch may complete no slice)
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

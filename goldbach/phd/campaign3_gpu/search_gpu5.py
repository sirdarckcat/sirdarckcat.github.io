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
import argparse, json, math, os, re, sys, time
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
                               split=args.deep_split, rg=args.deep_rg, max_rows=args.deep_max_rows, nthreads=256, log=lambda m: print(m, flush=True))
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


class MultiTester:
    """cq rows N0_v - q of every variant in the batch (shared M); test(idx, k) -> uint8 flags."""
    def __init__(self, specs, limbs=21):
        M = int(specs[0]["M"])
        assert all(int(s["M"]) == M for s in specs), "a pool needs one M"
        rows, self.off = [], []
        for s in specs:
            N0 = int(s["N0"])
            assert N0 > max(s["residual"]), "N0 - q must be positive"
            self.off.append(len(rows))
            rows.extend(to_limbs(N0 - int(q), limbs) for q in s["residual"])
        self.cq = cp.asarray(np.stack(rows))
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
            self.k(((T + threads - 1) // threads,), (threads,), (self.cq, self.M, idx, kv, out, np.int32(T)))
        return out


def run_pool(tester, kv, cnt, cols):
    """Members kv[m] with survivors cols[indptr[m]:indptr[m+1]] (global cq rows, ascending q).
    Returns per member: tests counted up to the first PRP, whether a PRP was found, success; and the
    tests computed on the GPU."""
    n = int(kv.size)
    indptr = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
    tests_m = cp.zeros(n, cp.int64)
    prp_m = cp.zeros(n, cp.bool_)
    succ_m = cnt == 0
    act = cp.nonzero(cnt > 0)[0]
    pos = cp.zeros(n, cp.int64)
    gtests = launches = 0
    while act.size:
        rem = cnt[act] - pos[act]
        D = int(max(1, min(args.dmax, int(rem.max()), args.target // int(act.size))))
        take = cp.minimum(rem, D)
        csum = cp.cumsum(take)
        total = int(csum[-1])
        m_of = cp.searchsorted(csum, cp.arange(total), side="right")
        off = cp.arange(total) - (csum - take)[m_of]
        ip = (indptr[act] + pos[act])[m_of] + off
        flags = tester.test(cols[ip], kv[act][m_of].astype(cp.uint32))
        if args.kernel == 28 and bool((flags > 1).any()):
            raise RuntimeError("kernel 28 flagged an n outside its range")
        big = D + 1
        first = cp.full(int(act.size), big, dtype=cp.int32)          # scatter_min: no int64
        cupyx.scatter_min(first, m_of, cp.where(flags == 1, off, big).astype(cp.int32))
        hit = first < big
        tests_m[act] += cp.where(hit, first.astype(cp.int64) + 1, take)
        prp_m[act[hit]] = True
        pos[act] += take
        done = (~hit) & (pos[act] == cnt[act])
        succ_m[act[done]] = True
        act = act[(~hit) & (~done)]
        gtests += total
        launches += 1
    return tests_m, prp_m, succ_m, gtests, launches


def run_batch(batch, out):
    """Sieve, select and test the slices in batch as one pool. Returns (lines, found, stats)."""
    t0 = time.time()
    tester = MultiTester(batch)
    L = args.block
    st = [dict(alive=0, hmk=0.0, hma=0.0, kdone=0, tests=0, prps=0, succ=[], kmax=0) for _ in batch]
    pool = []                                                    # (sid, kv, cnt, cols) chunks
    npool = [0]
    gt = [0, 0, 0.0]                                             # tests computed, launches, expected hits

    def flush():
        if not pool:
            return
        sid = cp.concatenate([cp.full(int(c[1].size), c[0], cp.int32) for c in pool])
        kv = cp.concatenate([c[1] for c in pool])
        cnt = cp.concatenate([c[2] for c in pool])
        cols = cp.concatenate([c[3] for c in pool])
        pool.clear(); npool[0] = 0
        tests_m, prp_m, succ_m, g, nl = run_pool(tester, kv, cnt, cols)
        gt[0] += g; gt[1] += nl
        tt, pp = int(tests_m.sum()), int(prp_m.sum())
        if tt:                                                   # expected successes of the tested members: sum (1 - p^)^count
            gt[2] += float(((1.0 - pp / tt) ** cnt.astype(cp.float64)).sum())
        for si in range(len(batch)):
            m = sid == si
            st[si]["tests"] += int(tests_m[m].sum())
            st[si]["prps"] += int(prp_m[m].sum())
            st[si]["succ"].extend(int(k) for k in kv[m & succ_m].tolist())

    K = 1 << args.klog
    for si, spec in enumerate(batch):
        fd = feeder_for(spec)
        kstart, kmax = spec["kstart"], spec["kmax"]
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        assert kstart % K == 0 and (kmax - kstart) % K == 0, "slices must be whole GPU sieve windows"
        st[si]["kmax"] = kmax
        for w0 in range(kstart, kmax, K):
            w = fd.window(w0)
            st[si]["alive"] += int(w.alive_total.sum())
            st[si]["kdone"] += K
            st[si]["hmk"] += float(w.hm_kept.sum()); st[si]["hma"] += float(w.hm_all.sum())
            pool.append((si, w.k.astype(cp.int64), w.cnt.astype(cp.int64), w.rows.astype(cp.int32) + np.int32(tester.off[si])))
            npool[0] += int(w.k.size)
            if npool[0] >= args.pool:
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
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches, expected hits {gt[2]:.4e}, found {len(found)} [v5 gpu-sieve]")
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
    while True:
        if not args.no_stop and os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
            print("C3GPU-HIT: found.jsonl is not empty", flush=True)
            return 3
        batch = []
        top = (args.kmax - 1) // args.slice * args.slice
        k0s = range(top, args.klo - 1, -args.slice) if args.desc else range(args.klo // args.slice * args.slice, args.kmax, args.slice)
        for k0 in k0s:
            for s in specs:
                name = f"{s['name']}@{k0}"
                if name not in done:
                    batch.append(dict(s, name=name, kstart=k0, kmax=min(k0 + args.slice, args.kmax)))
                    if len(batch) >= args.batch:
                        break
            if len(batch) >= args.batch:
                break
        if not batch:
            print("C3GPU-EXHAUSTED", flush=True)
            return 2
        lines, found, stats = run_batch(batch, out)
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

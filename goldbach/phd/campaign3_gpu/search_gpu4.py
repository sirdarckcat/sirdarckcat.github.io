#!/usr/bin/env python3
"""campaign3 on a GPU, version 4: search_gpu3.py with the sieve, the counts and the selection on the CPU, and only the
Fermat tests on the GPU. The CPU side is the uarch session's sieve200.Feeder (C, AVX-512 where available) on a thread
pool, and it prepares batch b+1 while the GPU tests batch b.

    python3 search_gpu4.py slices.json [--skip-frac F] [--kernel 28] [--threads N] [--sieve200 DIR] ...
    python3 search_gpu4.py --campaign DIR [--batch 32] [--kmax ...] [--klo ...] [--desc] [--no-stop] ...

Selection, accounting and log lines are search_gpu3.py's:
- per block of --block members (2^15 = search.run_block's blocks), the emptiest ceil(L(1-f)) by survivor count, ties by
  ascending k;
- hit% from the hit masses sum (1 - p_est)^count;
- tests counted up to each member's first base-2 PRP.
The Feeder computes the hit masses from the count histogram (equal to the GPU's sums to ~1e-12 relative).
check_v4.sh compares the slice lines with search_gpu3.py's on production slices. Successes are re-checked with
search.verify_success.
A window of 2^logK members is one CPU task. Slices must be whole windows: 2^20-member slices with logK <= 20.
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
ap.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 2) - 2), help="CPU sieve threads")
ap.add_argument("--logK", type=int, default=18, help="members per CPU task: 2^logK")
ap.add_argument("--sieve200", default=os.environ.get("SIEVE200_DIR", "/content/sieve200"), help="the uarch session's goldbach/sieve200")
ap.add_argument("--kernel", type=int, default=int(os.environ.get("SEARCH_GPU3_KERNEL", "2")), choices=(2, 3, 28),
                help="2: gpu_fermat.py (proven in Lean); 3: gpu_fermat3.py (dedicated squaring, lazy reduction, n < 2^(32L-7)); "
                     "28: the uarch session's gpu_fermat28.py (24 x 28-bit limbs, 'step_s1' with PTX mad.wide; n in [2^642, 2^668))")
args = ap.parse_args()
sys.path.insert(0, args.goldbach)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search                      # noqa: E402  (init_spec, verify_success)
from gmpy2 import mpz              # noqa: E402
import cupy as cp                  # noqa: E402
import cupyx                       # noqa: E402
from gpu_fermat import kernel as kernel2, to_limbs   # noqa: E402
from gpu_fermat3 import kernel as kernel3      # noqa: E402
import concurrent.futures, threading          # noqa: E402
sys.path.insert(0, args.sieve200)
from sieve200 import Feeder, Sieve200         # noqa: E402
if args.kernel == 28:
    sys.path.insert(0, os.environ.get("FERMAT28_DIR", "/content/f28"))
    import gpu_fermat28                       # noqa: E402

_VAR = {}
_VAR_LOCK = threading.Lock()
_TL = threading.local()
EXEC = concurrent.futures.ThreadPoolExecutor(max_workers=args.threads)
PRODUCER = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def load_specs(path):
    specs = json.load(open(path))
    for s in specs:
        for f in ("residual", "cover"):
            if isinstance(s.get(f), str):
                s[f] = json.loads(s[f])
    return specs


def ctx_for(spec):
    """One Sieve200 context per variant (primes to B, M^-1 and N0 mod each prime; a few MB), shared by the threads."""
    key = (spec["name"].split("@")[0], spec["N0"])
    with _VAR_LOCK:
        if key not in _VAR:
            _VAR[key] = Sieve200(int(spec["N0"]), int(spec["M"]), np.array(spec["residual"], dtype=np.uint32), args.sieve_b,
                                 logK=args.logK, exclude=[int(r) for r, _ in spec["cover"]])
        return _VAR[key]


def feed(si, spec, w0):
    """Sieve the 2^logK members from w0 with this thread's Feeder (one per row count, re-pointed at the variant)."""
    sv = ctx_for(spec)
    d = getattr(_TL, "fd", None)
    if d is None:
        d = _TL.fd = {}
    fd = d.get(sv.nU)
    if fd is None:
        fd = d[sv.nU] = Feeder(L=args.block, f=args.skip_frac, p_est=args.p_est, sv=sv)
    fd.sv = sv
    blocks = fd.window(w0)
    k = np.concatenate([np.asarray(fb.k, dtype=np.int64) for fb in blocks])
    cnt = np.concatenate([np.asarray(fb.cnt, dtype=np.int64) for fb in blocks])
    rows = np.concatenate([np.asarray(fb.rows, dtype=np.int32) for fb in blocks])
    return (si, k, cnt, rows, sum(int(fb.alive_total) for fb in blocks), sum(float(fb.hm_all) for fb in blocks),
            sum(float(fb.hm_kept) for fb in blocks), sv.K)


def produce(batch):
    """CPU side of a batch: every window of every slice through the thread pool. Returns per-slice chunks and statistics."""
    tasks = []
    per = [dict(chunks=[], alive=0, hma=0.0, hmk=0.0, kdone=0, kmax=0) for _ in batch]
    for si, spec in enumerate(batch):
        kstart, kmax = spec["kstart"], spec["kmax"]
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        per[si]["kmax"] = kmax
        K = 1 << args.logK
        assert kstart % K == 0 and (kmax - kstart) % K == 0, "slices must be whole CPU windows"
        tasks += [(si, spec, w0) for w0 in range(kstart, kmax, K)]
    for si, k, cnt, rows, al, ha, hk, K in EXEC.map(lambda t: feed(*t), tasks):
        p = per[si]
        p["chunks"].append((k, cnt, rows)); p["alive"] += al; p["hma"] += ha; p["hmk"] += hk; p["kdone"] += K
    return per


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
            self.k = gpu_fermat28.kernel(limbs, step_file="fermat28_step_s1.cuh", asm_mad=True)
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


def run_batch(batch, out, per, wall):
    """GPU side of a batch: test the members the CPU selected (per, from produce), as one pool in chunks of --pool members.
    wall: seconds the batch took end to end (shared out over its slices in the log line). Returns (lines, found, stats)."""
    tester = MultiTester(batch)
    st = [dict(alive=p["alive"], hmk=p["hmk"], hma=p["hma"], kdone=p["kdone"], kmax=p["kmax"], tests=0, prps=0, succ=[]) for p in per]
    gt = [0, 0, 0.0]                                             # tests computed, launches, expected hits
    chunks = [(si, k, cnt, rows) for si, p in enumerate(per) for (k, cnt, rows) in p["chunks"]]
    i = 0
    while i < len(chunks):                                       # pools of up to --pool members
        grp, n = [], 0
        while i < len(chunks) and (not grp or n + len(chunks[i][1]) <= args.pool):
            grp.append(chunks[i]); n += len(chunks[i][1]); i += 1
        sid = cp.asarray(np.concatenate([np.full(len(c[1]), c[0], dtype=np.int32) for c in grp]))
        kv = cp.asarray(np.concatenate([c[1] for c in grp]))
        cnt = cp.asarray(np.concatenate([c[2] for c in grp]))
        cols = cp.asarray(np.concatenate([c[3] + tester.off[c[0]] for c in grp]).astype(np.int32))
        if int(kv.size) == 0:
            continue
        tests_m, prp_m, succ_m, g, nl = run_pool(tester, kv, cnt, cols)
        gt[0] += g; gt[1] += nl
        tt, pp = int(tests_m.sum()), int(prp_m.sum())
        if tt:                                                   # expected successes of the tested members: sum (1 - p^)^count
            gt[2] += float(((1.0 - pp / tt) ** cnt.astype(cp.float64)).sum())
        for si in sorted(set(c[0] for c in grp)):
            m = sid == si
            st[si]["tests"] += int(tests_m[m].sum())
            st[si]["prps"] += int(prp_m[m].sum())
            st[si]["succ"].extend(int(k) for k in kv[m & succ_m].tolist())
    dt = wall / len(batch)
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
        lines.append(f"[{spec['name']}] k=[{spec['kstart']},{s['kmax']}) {dt:.0f}s ({kd/max(dt, 1e-9):.0f} k/s) tests={s['tests']} "
                     f"prp={s['prps']} p^={phat:.4f} alive/k={s['alive']/kd:.1f} E^={e_hat:.2f} "
                     f"hit%={100*hshare:.1f} found={nf}")
    tests = sum(s["tests"] for s in st)
    stats = (f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} batch {batch[0]['name']}..{batch[-1]['name']} "
             f"({len(batch)} slices) {wall:.1f}s: tests {tests} counted, {gt[0]} computed "
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches, expected hits {gt[2]:.4e}, found {len(found)} [v4 cpu-fed]")
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
    top = (args.kmax - 1) // args.slice * args.slice
    k0s = list(range(top, args.klo - 1, -args.slice) if args.desc else range(args.klo // args.slice * args.slice, args.kmax, args.slice))

    def next_batch(skip):
        batch = []
        for k0 in k0s:
            for s in specs:
                name = f"{s['name']}@{k0}"
                if name not in done and name not in skip:
                    batch.append(dict(s, name=name, kstart=k0, kmax=min(k0 + args.slice, args.kmax)))
                    if len(batch) >= args.batch:
                        return batch
        return batch

    cur = next_batch(set())
    fut = PRODUCER.submit(produce, cur) if cur else None
    t_last = time.time()
    while True:
        if not args.no_stop and os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
            print("C3GPU-HIT: found.jsonl is not empty", flush=True)
            return 3
        if not cur:
            print("C3GPU-EXHAUSTED", flush=True)
            return 2
        per = fut.result()
        nxt = next_batch(set(b["name"] for b in cur))
        fut = PRODUCER.submit(produce, nxt) if nxt else None        # the CPU sieves the next batch while the GPU tests this one
        lines, found, stats = run_batch(cur, out, per, 0.0)
        wall = time.time() - t_last; t_last = time.time()
        lines = [re.sub(r"\) 0s \(\d+ k/s\)", f") {wall/len(cur):.0f}s ({(args.slice*len(cur))/max(wall,1e-9):.0f} k/s)", l) for l in lines]
        stats = stats.replace(" 0.0s: tests", f" {wall:.1f}s: tests")
        with open(LOG, "a") as f:
            f.write("\n".join(lines) + "\n")
        with open(STATS, "a") as f:
            f.write(stats + "\n")
        done.update(b["name"] for b in cur)
        cur = nxt


def main():
    if args.campaign:
        sys.exit(campaign(args.campaign))
    specs = load_specs(args.specs)
    out = open(args.out, "a")
    for i in range(0, len(specs), args.batch):
        batch = specs[i:i + args.batch]
        t0 = time.time()
        per = produce(batch)
        lines, found, stats = run_batch(batch, out, per, 0.0)
        wall = time.time() - t0
        lines = [re.sub(r"\) 0s \(\d+ k/s\)", f") {wall/len(batch):.0f}s ({sum(p['kdone'] for p in per)/max(wall,1e-9):.0f} k/s)", l) for l in lines]
        print("\n".join(lines), flush=True)
        print("#", stats.replace(" 0.0s: tests", f" {wall:.1f}s: tests"), flush=True)


if __name__ == "__main__":
    main()

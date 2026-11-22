#!/usr/bin/env python3
"""campaign3 on a GPU, version 3: the sieve and the tests on the GPU, the tests pooled across a batch of slices.

    python3 search_gpu3.py slices.json [--skip-frac F] [--p-est 0.055] [--out found.jsonl] [--goldbach DIR]
    python3 search_gpu3.py --campaign DIR [--batch 16] [--kmax 450000000] [--skip-frac F] ...

Why: in search_gpu2.py each block's members are tested on their own. A launch then holds too few
members, so it tests up to target/members complements of each, most of them after the member's
first PRP. On the L4 that wasted 41% of the tests computed at --skip-frac 0, and 93% at 0.97.
Here every batch of slices is one pool. All campaign3 variants share M, so one tester holds every
variant's N0 - q. A launch tests at most --dmax complements of a member, and up to --target tests.

Sieve: search_gpu2.py's kernel, except that A = (q - N0 mod s) * M^-1 mod s is computed in the
thread instead of read from a |U| x pi(B) table, so a variant costs only its N0 mod s (cached).
check_v3.py compares the alive matrix with search.run_block's sieve.

Selection: as search.run_block. With --skip-frac f, a block's members are sorted by survivor count
(stable) and the first ceil((1-f)L) are tested; hit% is the hit mass sum (1-p)^count they keep.
Each member's survivors are tested in ascending residual order and it stops at its first base-2
PRP. Tests are counted up to that PRP, so per slice the tests, PRPs, alive/k, hit% and successes
equal search_gpu2.py's and search.run_block's for the same parameters (check_v3.py).

Successes are re-checked on the CPU with search.verify_success. Output is search.py's line per
slice. A slice's seconds are its batch's time divided by the number of slices in the batch.

Campaign mode reads DIR/my_specs.json and skips the slices already in DIR/search.log (2^20 k each,
k-major order, from --klo up to --kmax, or downwards with --desc: E falls as N grows, so the slices
just below the 199-digit ceiling give the most hits per k). It appends a line per slice to DIR/search.log once its batch is done, and statistics
to DIR/gpu3_stats.log. It stops on a hit (exit 3, DIR/found.jsonl not empty; with --no-stop it goes on)
or when every variant reaches --kmax (exit 2).
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
args = ap.parse_args()
sys.path.insert(0, args.goldbach)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search                      # noqa: E402  (init_spec, verify_success)
from gmpy2 import mpz              # noqa: E402
import cupy as cp                  # noqa: E402
import cupyx                       # noqa: E402
from gpu_fermat import kernel, to_limbs   # noqa: E402

SIEVE_SRC = r'''
extern "C" __global__ void sieve3(const int *U, const int *S, const int *inv, const int *n0m, const int *kmod,
                                  long long nS, long long nU, int L, unsigned char *alive) {
    long long t = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= nS * nU) return;
    long long q = t / nS, si = t - q * nS;
    int s = S[si];
    int d = U[q] % s - n0m[si];                                    /* q - N0 (mod s) */
    if (d < 0) d += s;
    int a = (int)(((unsigned long long)d * (unsigned)inv[si]) % (unsigned)s);   /* k == a (mod s): s | N0 + kM - q */
    int j = a - kmod[si];
    if (j < 0) j += s;
    unsigned char *row = alive + q * (long long)L;
    for (; j < L; j += s) row[j] = 0;
}
'''
_SK = cp.RawKernel(SIEVE_SRC, "sieve3")
_VAR = {}                           # variant name -> (U, n0m) on the GPU
_SHARED = {}


def load_specs(path):
    specs = json.load(open(path))
    for s in specs:
        for f in ("residual", "cover"):
            if isinstance(s.get(f), str):
                s[f] = json.loads(s[f])
    return specs


def variant_state(spec):
    base = spec["name"].split("@")[0]
    key = (base, spec["N0"])
    if key not in _VAR:
        search.init_spec(spec, args.sieve_b, args.block)       # S, M^-1 mod s cached per M; N0 mod s per call
        G = search.G
        if "S" not in _SHARED or _SHARED["M"] != spec["M"]:
            _SHARED.update(M=spec["M"], S=cp.asarray(G["S"].astype(np.int32)), inv=cp.asarray(G["inv"].astype(np.int32)),
                           S64=cp.asarray(G["S"].astype(np.int64)))
        assert int(G["S"].max()) < 2**31 and int(min(G["U"])) > 0
        _VAR[key] = (cp.asarray(np.array(G["U"], dtype=np.int32)), cp.asarray(G["n0m"].astype(np.int32)))
    return _VAR[key]


def sieve_block(U, n0m, k0, L):
    S, inv, S64 = _SHARED["S"], _SHARED["inv"], _SHARED["S64"]
    nU, nS = int(U.size), int(S.size)
    alive = cp.ones((nU, L), dtype=cp.uint8)
    kmod = (k0 % S64).astype(cp.int32)
    T = nU * nS
    _SK(((T + 255) // 256,), (256,), (U, S, inv, n0m, kmod, np.int64(nS), np.int64(nU), np.int32(L), alive))
    return alive


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
        self.k = kernel(limbs)

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
        big = D + 1
        first = cp.full(int(act.size), big, dtype=cp.int32)          # scatter_min: no int64
        cupyx.scatter_min(first, m_of, cp.where(flags.astype(cp.bool_), off, big).astype(cp.int32))
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
    gt = [0, 0]

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
        for si in range(len(batch)):
            m = sid == si
            st[si]["tests"] += int(tests_m[m].sum())
            st[si]["prps"] += int(prp_m[m].sum())
            st[si]["succ"].extend(int(k) for k in kv[m & succ_m].tolist())

    for si, spec in enumerate(batch):
        U, n0m = variant_state(spec)
        kstart, kmax = spec["kstart"], spec["kmax"]
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        st[si]["kmax"] = kmax
        for k0 in range(kstart, kmax, L):
            Lb = min(L, kmax - k0)
            alive = sieve_block(U, n0m, k0, Lb)                     # (|U|, Lb) uint8
            counts = alive.sum(axis=0, dtype=cp.int32)
            st[si]["alive"] += int(counts.sum())
            st[si]["kdone"] += Lb
            if args.skip_frac > 0:
                w = (1.0 - args.p_est) ** counts.astype(cp.float64)
                keep = int(math.ceil(Lb * (1.0 - args.skip_frac)))
                order = cp.lexsort(cp.stack([cp.arange(Lb), counts]))[:keep]   # stable by count
                st[si]["hmk"] += float(w[order].sum()); st[si]["hma"] += float(w.sum())
            else:
                order = cp.arange(Lb)
                st[si]["hmk"] += 1.0; st[si]["hma"] += 1.0
            sub = cp.ascontiguousarray(alive[:, order].T)          # (keep, |U|)
            _, cols = cp.nonzero(sub)                               # by member, then ascending q
            pool.append((si, (k0 + order).astype(cp.int64), counts[order].astype(cp.int64),
                         cols.astype(cp.int32) + tester.off[si]))
            npool[0] += int(order.size)
            del alive, sub
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
             f"(waste {100*(1-tests/max(gt[0],1)):.1f}%), {gt[1]} launches")
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

#!/usr/bin/env python3
"""search.py for campaign3-style specs with the sieve AND the Fermat tests on the GPU.

    python3 search_gpu2.py slices.json [--procs 11] [--sieve-b 1000000] [--block 32768]
                          [--skip-frac 0] [--p-est 0.055] [--out found.jsonl] [--goldbach DIR]

The sieve runs on the GPU: for every residual q and sieve prime s (search.init_spec's primes,
inverses and N0 residues), A[q, s] = (q - N0 mod s) * M^-1 mod s is computed once per spec, and per
block one thread per (q, s) clears k = A - k0 (mod s), A - k0 + s, ... in row q, which is what
search.run_block's sieve does on the CPU (check_sieve.py compares the two matrices). The main process tests on the
GPU (gpu_fermat.Tester): each launch tests the next D complements of every member still open,
in ascending residual order as search.run_block does, and a member stops at its first base-2
probable prime. Tests are counted up to that PRP, so with --skip-frac 0 the per-block tests,
prps and successes equal search.run_block's (checked by check_block.py). --skip-frac f tests
only the emptiest (1-f) of each block (stable order by survivor count) with search.py's hit-mass
accounting. Successes are re-checked on the CPU with search.verify_success. Output: search.py's
per-slice line, so campaign logs and statistics carry over.
"""
import argparse, json, math, os, sys, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("specs")
ap.add_argument("--procs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
ap.add_argument("--block", type=int, default=32768)
ap.add_argument("--sieve-b", type=int, default=1000000)
ap.add_argument("--skip-frac", type=float, default=0.0)
ap.add_argument("--p-est", type=float, default=0.055)
ap.add_argument("--out", default="found.jsonl")
ap.add_argument("--goldbach", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ap.add_argument("--target", type=int, default=262144, help="tests per GPU launch")
args = ap.parse_args()
sys.path.insert(0, args.goldbach)
import search                      # noqa: E402  (init_spec, G, verify_success)
from gmpy2 import mpz              # noqa: E402

SPECS = json.load(open(args.specs))
for _s in SPECS:                   # parse list fields given as JSON text, before the workers fork
    for _f in ("residual", "cover"):
        if isinstance(_s.get(_f), str):
            _s[_f] = json.loads(_s[_f])
_cur = {"name": None}


SIEVE_SRC = r'''
extern "C" __global__ void sieve(const int *A, const int *S, const int *kmod, long long nS, long long nU,
                                 int L, unsigned char *alive) {
    long long t = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= nS * nU) return;
    long long q = t / nS, si = t - q * nS;
    int s = S[si];
    int j = A[t] - kmod[si];
    if (j < 0) j += s;
    unsigned char *row = alive + q * (long long)L;
    for (; j < L; j += s) row[j] = 0;
}
'''


class GpuSieve:
    def __init__(self, spec, cp):
        search.init_spec(spec, args.sieve_b, args.block)
        G = search.G
        self.cp = cp
        self.U = cp.asarray(np.array(G["U"], dtype=np.int64))
        self.S = cp.asarray(G["S"].astype(np.int64))
        n0m = cp.asarray(G["n0m"].astype(np.int64))
        inv = cp.asarray(G["inv"].astype(np.int64))
        A = ((self.U[:, None] - n0m[None, :]) % self.S[None, :]) * inv[None, :] % self.S[None, :]
        self.A = cp.ascontiguousarray(A.astype(cp.int32))          # (|U|, |S|), entries < s < 2^31
        self.S32 = self.S.astype(cp.int32)
        self.k = cp.RawKernel(SIEVE_SRC, "sieve")
        self.nU, self.nS = int(self.U.size), int(self.S.size)

    def block(self, k0, L):
        cp = self.cp
        alive = cp.ones((self.nU, L), dtype=cp.uint8)
        kmod = (k0 % self.S).astype(cp.int32)
        T = self.nU * self.nS
        self.k(((T + 255) // 256,), (256,), (self.A, self.S32, kmod, np.int64(self.nS), np.int64(self.nU), np.int32(L), alive))
        return alive


def main():
    import cupy as cp
    import cupyx
    from gpu_fermat import Tester
    L = args.block
    out = open(args.out, "a")
    for si, spec in enumerate(SPECS):
        t0 = time.time()
        U = spec["residual"]
        tester = Tester(mpz(spec["N0"]), mpz(spec["M"]), U)
        gs = GpuSieve(spec, cp)
        kmax, kstart = spec.get("kmax"), spec.get("kstart", 0)
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        blocks = list(range(kstart, kmax, L))
        tests = prps = alive_sum = 0
        hm_kept = hm_all = 0.0
        found = []
        for k0 in blocks:
            alive = gs.block(k0, L).astype(cp.bool_)
            aliveT = cp.ascontiguousarray(alive.T)                       # (L, |U|)
            counts = aliveT.sum(axis=1).astype(cp.int64)
            alive_sum += int(counts.sum())
            if args.skip_frac > 0:
                w = (1.0 - args.p_est) ** counts.astype(cp.float64)
                keep = int(math.ceil(L * (1.0 - args.skip_frac)))
                order = cp.lexsort(cp.stack([cp.arange(L), counts]))[:keep]   # stable by count
                hm_kept += float(w[order].sum()); hm_all += float(w.sum())
            else:
                order = cp.arange(L)
                hm_kept += 1.0; hm_all += 1.0
            sub = aliveT[order]
            cnt = counts[order]
            rows, cols = cp.nonzero(sub)                                   # sorted by row, then col
            indptr = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt)])
            cols = cols.astype(cp.int32)
            succ = (k0 + order[cnt == 0]).tolist()
            act = cp.nonzero(cnt > 0)[0]
            pos = cp.zeros(order.size, cp.int64)
            while act.size:
                rem = cnt[act] - pos[act]
                D = int(max(1, min(int(rem.max()), args.target // int(act.size))))
                take = cp.minimum(rem, D)
                csum = cp.cumsum(take)
                total = int(csum[-1])
                m_of = cp.searchsorted(csum, cp.arange(total), side="right")
                off = cp.arange(total) - (csum - take)[m_of]
                ip = (indptr[act] + pos[act])[m_of] + off
                flags = tester.test(cols[ip], (k0 + order[act])[m_of].astype(cp.uint32))
                big = D + 1
                first = cp.full(int(act.size), big, dtype=cp.int32)          # scatter_min: no int64
                cupyx.scatter_min(first, m_of, cp.where(flags.astype(cp.bool_), off, big).astype(cp.int32))
                hit = first < big
                tests += int(cp.where(hit, first + 1, take).sum())
                prps += int(hit.sum())
                pos[act] += take
                done = (~hit) & (pos[act] == cnt[act])
                succ.extend((k0 + order[act[done]]).tolist())
                act = act[(~hit) & (~done)]
            for k in succ:
                res = search.verify_success(spec, int(k))
                if res:
                    res["name"] = spec["name"]
                    found.append(res)
                    print(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} g={res['g']}", flush=True)
                    out.write(json.dumps(res) + "\n"); out.flush()
            if found and spec.get("stop_on_success"):
                break
        dt = time.time() - t0
        kdone = len(blocks) * L
        phat = prps / tests if tests else 0.0
        e_hat = (alive_sum / kdone) * phat if kdone else 0.0
        hshare = hm_kept / hm_all if hm_all else 1.0
        print(f"[{spec['name']}] k=[{kstart},{kmax}) {dt:.0f}s ({kdone/dt:.0f} k/s) tests={tests} prp={prps} "
              f"p^={phat:.4f} alive/k={alive_sum/max(kdone,1):.1f} E^={e_hat:.2f} "
              f"hit%={100*hshare:.1f} found={len(found)}", flush=True)
        if found and spec.get("stop_on_success"):
            break


if __name__ == "__main__":
    main()

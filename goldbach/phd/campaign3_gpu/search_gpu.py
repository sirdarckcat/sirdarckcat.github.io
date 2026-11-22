#!/usr/bin/env python3
"""search.py for campaign3-style specs with the Fermat tests on the GPU.

    python3 search_gpu.py slices.json [--procs 11] [--sieve-b 1000000] [--block 32768]
                          [--skip-frac 0] [--p-est 0.055] [--out found.jsonl] [--goldbach DIR]

Worker processes sieve blocks exactly as search.run_block does (same code, search.init_spec's
primes and inverses) and return the alive matrix packed as bits. The main process tests on the
GPU (gpu_fermat.Tester): each launch tests the next D complements of every member still open,
in ascending residual order as search.run_block does, and a member stops at its first base-2
probable prime. Tests are counted up to that PRP, so with --skip-frac 0 the per-block tests,
prps and successes equal search.run_block's (checked by check_block.py). --skip-frac f tests
only the emptiest (1-f) of each block (stable order by survivor count) with search.py's hit-mass
accounting. Successes are re-checked on the CPU with search.verify_success. Output: search.py's
per-slice line, so campaign logs and statistics carry over.
"""
import argparse, json, math, os, sys, time
from multiprocessing import Pool
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


def sieve_task(task):
    si, k0 = task
    spec = SPECS[si]
    if _cur["name"] != spec["name"]:
        search.init_spec(spec, args.sieve_b, args.block)      # primes/inverses cached per M
        _cur["name"] = spec["name"]
    G = search.G
    U, L = G["U"], G["block"]
    Ss_list = G["S_small_list"]
    S, n0m, inv, small = G["S"], G["n0m"], G["inv"], G["small"]
    alive = np.ones((len(U), L), dtype=bool)                   # identical to search.run_block
    for i, q in enumerate(U):
        row = alive[i]
        kres = ((q - n0m) * inv - k0) % S
        js = kres[small].tolist()
        for j, s in zip(js, Ss_list):
            row[j::s] = False
        jl = kres[~small]
        hit = jl < L
        row[jl[hit]] = False
    return si, k0, np.packbits(alive, axis=1)


def main():
    import cupy as cp
    import cupyx
    from gpu_fermat import Tester
    L = args.block
    out = open(args.out, "a")
    pool = Pool(args.procs)
    for si, spec in enumerate(SPECS):
        t0 = time.time()
        U = spec["residual"]
        tester = Tester(mpz(spec["N0"]), mpz(spec["M"]), U)
        kmax, kstart = spec.get("kmax"), spec.get("kstart", 0)
        if spec.get("ceiling_digits"):
            kcap = int((mpz(10) ** spec["ceiling_digits"] - mpz(spec["N0"])) // mpz(spec["M"]))
            kmax = min(kmax, kcap + 1)
        blocks = list(range(kstart, kmax, L))
        tests = prps = alive_sum = 0
        hm_kept = hm_all = 0.0
        found = []
        for _, k0, packed in pool.imap(sieve_task, [(si, b) for b in blocks]):
            alive = cp.unpackbits(cp.asarray(packed).ravel()).reshape(len(U), L).astype(cp.bool_)   # rows of L bits, L % 8 == 0
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
    pool.terminate()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Window-mode progression search (v2).

For each window [T, T+W) of t values:
  1. numpy presieve: for every presieve prime s (not a modulus) and every
     residual p_i, kill t where s | N0 + t*M - p_i  (t ≡ t0(i,s) mod s).
     survivors[t] = count of residuals with no presieve factor.
  2. process t in ascending-survivor order: fail-fast SPRP(base 2) over the
     surviving residuals of that t; if all composite -> scan for first prime
     complement q > Q among uncovered primes; report hit.
Deterministic, resumable, parallel by window striping.
"""
import argparse, json, math, os, sys, time
import multiprocessing as mp
import numpy as np
import gmpy2
from gmpy2 import mpz

def prime_sieve(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i*i::i] = False
    return np.nonzero(s)[0]

def crt(classes):
    M = mpz(1); N0 = mpz(0)
    for r, b in classes:
        r = mpz(r); b = mpz(b)
        inv = gmpy2.invert(M % r, r)
        N0 = N0 + M * ((b - N0) % r * inv % r)
        M *= r
    return N0 % M, M

def worker(wid, nw, args, cov, out_q, stop_ev):
    classes = [(int(r), int(b)) for r, b in cov["classes"]]
    residual = np.array(sorted(int(p) for p in cov["residual"]), dtype=np.int64)
    kres = len(residual)
    Q = cov["Q"]
    N0, M = crt([(2, 0)] + classes)
    Nmax = None
    if args.max_digits: Nmax = mpz(10) ** args.max_digits
    if args.nmax:
        nm = mpz(args.nmax)
        Nmax = nm if Nmax is None else min(Nmax, nm)
    used = set(r for r, _ in classes); used.add(2)
    ps = np.array([s for s in prime_sieve(args.presieve) if int(s) not in used],
                  dtype=np.int64)  # s=2 excluded via 'used' (complements are odd)
    # t0(i,s): smallest t>=0 with s | N0 + t*M - p_i  => t ≡ (p_i-N0)*M^{-1} (mod s)
    Minv = np.array([int(gmpy2.invert(int(M % int(s)), int(s))) for s in ps], dtype=np.int64)
    N0m = np.array([int(N0 % int(s)) for s in ps], dtype=np.int64)
    t0_blocks = []
    for lo in range(0, len(ps), 4096):                        # block to bound memory
        pb = ps[lo:lo+4096]
        pim = residual[None, :] % pb[:, None]                 # (S_b, k)
        blk = ((pim - N0m[lo:lo+4096, None]) % pb[:, None]) * Minv[lo:lo+4096, None] % pb[:, None]
        t0_blocks.append(blk.astype(np.int64))
    t0 = np.concatenate(t0_blocks); del t0_blocks             # (S, k) first-hit t per (s, residual)
    res_mpz = [mpz(int(p)) for p in residual]
    # uncovered q candidates above Q
    qc = []
    for qq in prime_sieve(args.qmax):
        qq = int(qq)
        if qq > Q and all((qq - b) % r for r, b in classes):
            qc.append(qq)
    W = args.window
    small = ps < W                                       # primes with multiple hits/window
    ps_s, t0_s = ps[small], t0[small]
    ps_l, t0_l = ps[~small], t0[~small]
    Sflat_l = np.repeat(ps_l, kres)
    t0flat_l = t0_l.ravel()
    iflat_l = np.tile(np.arange(kres, dtype=np.int64), len(ps_l))
    idxk = np.arange(kres)
    tested = 0; t_start = time.time()
    win = args.t_lo + wid * W
    while win < args.t_hi and not stop_ev.is_set():
        if Nmax is not None and N0 + win * M >= Nmax:
            break
        alive = np.ones((W, kres), dtype=bool)
        # small primes: stride over the window, vectorized across residuals
        for j in range(len(ps_s)):
            s = int(ps_s[j])
            row = (t0_s[j] - win) % s                    # first offset per residual
            for m in range(0, W, s):
                idx = row + m
                v = idx < W
                alive[idx[v], idxk[v]] = False
                if s >= W: break
        # large primes: at most one hit each
        off = (t0flat_l - win) % Sflat_l
        hm = off < W
        alive[off[hm], iflat_l[hm]] = False
        surv = alive.sum(axis=1)
        if args.select_frac < 1.0:
            thr = np.quantile(surv, args.select_frac)
            sel = np.nonzero(surv <= thr)[0]
            order = sel[np.argsort(surv[sel], kind="stable")]
        else:
            order = np.argsort(surv, kind="stable")
        for tt in order:
            t = win + int(tt)
            if t >= args.t_hi: continue
            N = N0 + t * M
            if Nmax is not None and N >= Nmax: continue
            ok = True
            for i in np.nonzero(alive[tt])[0]:
                if gmpy2.is_strong_prp(N - res_mpz[i], 2):
                    ok = False; break
            tested += 1
            if ok:
                hit = None
                for qq in qc:
                    c = N - qq
                    if gmpy2.is_strong_prp(c, 2) and gmpy2.is_bpsw_prp(c):
                        hit = qq; break
                out_q.put(("HIT", wid, t, hit, str(N), tested, time.time() - t_start))
                if hit is not None:
                    stop_ev.set(); return
            if tested % args.report == 0:
                out_q.put(("prog", wid, t, None, "", tested, time.time() - t_start))
                if stop_ev.is_set(): return
        win += nw * W
    out_q.put(("done", wid, win, None, "", tested, time.time() - t_start))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", required=True)
    ap.add_argument("--t-lo", type=int, default=1)
    ap.add_argument("--t-hi", type=int, default=10**12)
    ap.add_argument("--max-digits", type=int, default=0)
    ap.add_argument("--nmax", type=str, default="")
    ap.add_argument("--presieve", type=int, default=10**6)
    ap.add_argument("--window", type=int, default=1 << 14)
    ap.add_argument("--qmax", type=int, default=2 * 10**6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--report", type=int, default=5000)
    ap.add_argument("--select-frac", type=float, default=1.0,
                    help="only PRP-test this fraction of t (lowest presieve-survivor counts)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cov = json.load(open(args.cover))
    out_q = mp.Queue(); stop_ev = mp.Event()
    procs = [mp.Process(target=worker, args=(w, args.workers, args, cov, out_q, stop_ev))
             for w in range(args.workers)]
    for p in procs: p.start()
    t0 = time.time(); total = {}; hits = []; done = 0
    while done < len(procs) and not (hits and hits[-1]["q"]):
        msg, wid, t, q, N, tested, el = out_q.get()
        total[wid] = tested
        if msg == "prog":
            tot = sum(total.values())
            print(f"[{time.time()-t0:7.0f}s] tested={tot} rate={tot/(time.time()-t0):.1f}/s t~{t}", flush=True)
        elif msg == "HIT":
            hits.append({"t": t, "q": q, "N": N})
            print(f"[HIT] t={t} q={q} (worker {wid})", flush=True)
        elif msg == "done":
            done += 1
    stop_ev.set()
    for p in procs: p.join(timeout=10)
    for p in procs:
        if p.is_alive(): p.terminate()
    json.dump({"hits": hits, "tested": sum(total.values())}, open(args.out, "w"))
    print(f"[search done] hits={len(hits)} tested={sum(total.values())}", flush=True)

if __name__ == "__main__":
    main()

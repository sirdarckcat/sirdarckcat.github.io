#!/usr/bin/env python3
"""Progression search for the Goldbach-gap construction.

Given a cover (classes [(r, b_r)], residual primes k list, target Q):
  M = prod r,  N0 = CRT(b_r mod r, 0 mod 2)  (N even)
  For t = t_lo..t_hi:  N = N0 + t*M   (skip N > Nmax if given)
    - light presieve: for small primes s NOT in the modulus set, N mod s == p mod s
      for residual p => s | N-p => that residual is composite, skip its PRP.
    - fail fast: PRP-test surviving residuals (base-2 strong PRP, then a couple
      more bases only when all pass); if ANY residual complement is a probable
      prime, t fails.
    - if all residual complements composite: scan primes q > Q (skipping covered
      classes) for first N-q probable prime  => candidate (t, q). Also verify
      every uncovered prime in (Q, q) has composite complement (part of scan).
Writes JSON result and exits after first success.
Parallel: worker processes take stripes of t.
"""
import argparse, json, math, sys, time
import multiprocessing as mp
import gmpy2
from gmpy2 import mpz

def prime_sieve(n):
    import numpy as np
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i*i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]

def crt(classes):
    M = mpz(1); N0 = mpz(0)
    for r, b in classes:
        r = mpz(r); b = mpz(b)
        g = gmpy2.invert(M % r, r)
        N0 = N0 + M * ((b - N0) % r * g % r)
        M *= r
    return N0 % M, M

def is_comp(n):
    """True iff n is composite, by strong PRP base 2 (one-sided proof)."""
    return not gmpy2.is_strong_prp(n, 2)

def worker(wid, nw, args, cov, out_q, stop_ev):
    classes = [(int(r), int(b)) for r, b in cov["classes"]]
    residual = [int(p) for p in cov["residual"]]
    Q = cov["Q"]
    all_classes = [(2, 0)] + classes
    N0, M = crt(all_classes)
    Nmax = mpz(10) ** args.max_digits if args.max_digits else None
    if args.nmax: Nmax = min(Nmax, mpz(args.nmax)) if Nmax else mpz(args.nmax)
    # presieve primes: small primes not used as moduli
    used = set(r for r, _ in all_classes)
    ps = [s for s in prime_sieve(args.presieve) if s not in used and s > 2]
    # bucket[s][b] = list of residual indices i with residual[i] ≡ b (mod s)
    bucket = {}
    for s in ps:
        d = {}
        for i, p in enumerate(residual):
            d.setdefault(p % s, []).append(i)
        bucket[s] = d
    M_mod = {s: int(M % s) for s in ps}
    N0_mod = {s: int(N0 % s) for s in ps}
    res_mpz = [mpz(p) for p in residual]
    kres = len(residual)
    # q-scan primes above Q (uncovered only)
    qcands = []
    for q in prime_sieve(args.qmax):
        if q > Q:
            if all((q - b) % r for r, b in classes):
                qcands.append(q)
    tested = 0; t = args.t_lo + wid
    t0 = time.time()
    while t < args.t_hi and not stop_ev.is_set():
        N = N0 + t * M
        if Nmax and N >= Nmax: break
        # presieve: s | N - residual[i]  iff  residual[i] ≡ N (mod s)
        alive = [True] * kres
        for s in ps:
            nm = (N0_mod[s] + t * M_mod[s]) % s
            for i in bucket[s].get(nm, ()):
                alive[i] = False
        ok = True
        for i in range(kres):
            if alive[i] and not is_comp(N - res_mpz[i]):
                ok = False; break
        tested += 1
        if ok:
            # all residuals < Q composite. scan for first prime complement q > Q
            hit = None
            for q in qcands:
                c = N - q
                if gmpy2.is_strong_prp(c, 2) and gmpy2.is_bpsw_prp(c):
                    hit = q; break
            out_q.put(("HIT", wid, t, hit, str(N), tested, time.time() - t0))
            if hit is not None:
                stop_ev.set(); return
        if tested % args.report == 0:
            out_q.put(("prog", wid, t, None, "", tested, time.time() - t0))
        t += nw
    out_q.put(("done", wid, t, None, "", tested, time.time() - t0))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", required=True)
    ap.add_argument("--t-lo", type=int, default=1)
    ap.add_argument("--t-hi", type=int, default=10**12)
    ap.add_argument("--max-digits", type=int, default=0, help="require N < 10^this")
    ap.add_argument("--nmax", type=str, default="", help="require N < this integer")
    ap.add_argument("--presieve", type=int, default=1000)
    ap.add_argument("--qmax", type=int, default=2 * 10**6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--report", type=int, default=2000)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cov = json.load(open(args.cover))
    out_q = mp.Queue(); stop_ev = mp.Event()
    procs = [mp.Process(target=worker, args=(w, args.workers, args, cov, out_q, stop_ev))
             for w in range(args.workers)]
    for p in procs: p.start()
    t0 = time.time(); total = {}; hits = []
    done = 0
    while done < len(procs):
        msg, wid, t, q, N, tested, el = out_q.get()
        total[wid] = tested
        if msg == "prog":
            tot = sum(total.values())
            print(f"[{time.time()-t0:7.0f}s] tested={tot} rate={tot/(time.time()-t0):.1f}/s t~{t}", flush=True)
        elif msg == "HIT":
            hits.append({"t": t, "q": q, "N": N})
            print(f"[HIT] t={t} q={q} (worker {wid})", flush=True)
            if q is not None: done = len(procs)  # stop_ev set; workers will exit
        elif msg == "done":
            done += 1
    for p in procs: p.join(timeout=5)
    for p in procs:
        if p.is_alive(): p.terminate()
    json.dump({"hits": hits, "tested": sum(total.values())}, open(args.out, "w"))
    print(f"[search done] hits={len(hits)} tested={sum(total.values())}", flush=True)

if __name__ == "__main__":
    main()

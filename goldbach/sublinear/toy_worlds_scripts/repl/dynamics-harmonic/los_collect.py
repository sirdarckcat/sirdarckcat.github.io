#!/usr/bin/env python3
"""Real 200-digit data for the neighbour-row tests: random members of the real 200,000 cover, rows sieved by every prime
467..10^6, every surviving row Fermat-tested (base 2).  Output los_data.npz: k (members), ptr, rowidx, isprime."""
import sys, time, math, numpy as np, gmpy2
from common import setup
cov, rows, N0, M, K = setup(); Q = 200000; Z = 10 ** 6
nm = int(sys.argv[1]) if len(sys.argv) > 1 else 200; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sv = np.ones(Z + 1, bool); sv[:2] = False
for i in range(2, int(Z ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
PR = np.nonzero(sv)[0]; PR = PR[PR >= 467].astype(np.int64)
n0 = np.array([int(gmpy2.f_mod(gmpy2.mpz(N0), int(r))) for r in PR], dtype=np.int64)
mm = np.array([int(gmpy2.f_mod(gmpy2.mpz(M), int(r))) for r in PR], dtype=np.int64)
rowid = -np.ones(Q, dtype=np.int64); rowid[rows] = np.arange(len(rows))
rng = np.random.default_rng(seed); ks = np.sort(rng.choice(K, nm, replace=False))
ptr = [0]; ridx = []; flags = []; t0 = time.time(); ntest = 0
nsmall = int(np.searchsorted(PR, Q))
for k in ks:
    k = int(k); c = (n0 + k * mm) % PR                 # N mod r
    struck = np.zeros(len(rows), bool)
    j = 0
    while True:
        lim = nsmall if j else len(PR)
        if j: lim = int(np.searchsorted(PR, Q // j + 1))
        if lim == 0: break
        cand = c[:lim] + j * PR[:lim]; cand = cand[cand < Q]
        if j and len(cand) == 0 and PR[0] * j >= Q: break
        hit = rowid[cand]; struck[hit[hit >= 0]] = True
        j += 1
        if 467 * j >= Q: break
    surv = np.nonzero(~struck)[0]; N = gmpy2.mpz(N0) + k * gmpy2.mpz(M)
    fl = np.zeros(len(surv), bool)
    for i, s in enumerate(surv):
        n = N - int(rows[s]); fl[i] = gmpy2.powmod(2, n - 1, n) == 1
    ntest += len(surv); ridx.append(surv); flags.append(fl); ptr.append(ptr[-1] + len(surv))
print(f"members {nm} tests {ntest} primes {sum(int(f.sum()) for f in flags)} time {time.time() - t0:.1f}s", flush=True)
np.savez(f"los_data_{seed}.npz", k=ks, ptr=np.array(ptr), rowidx=np.concatenate(ridx), isprime=np.concatenate(flags))

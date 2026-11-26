#!/usr/bin/env python3
"""Real members of the real 200,000 cover: sieve every row to 10^8, Fermat-test EVERY surviving row.
   usage: gen_rows.py seed nmembers out.npz
   Output per member: k, per row: least prime factor <= 10^8 (0 if none), Fermat result for survivors."""
import sys, os, math, time, numpy as np, gmpy2
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
seed, nmem, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
Q = 200000; Z = 10**8
f = cr.S + "q200000_m89.txt"
line = [x for x in open(f) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows, p = cr.load(f); rows = rows[rows < Q].astype(np.int64)
assert len(rows) == 1502, len(rows)
M = 2
for r, a in cov: M *= r
# CRT, even
N0 = 0; mod = 1
for r, a in [(2, 0)] + cov:
    t = ((a - N0) * pow(mod, -1, r)) % r
    N0 += mod * t; mod *= r
assert mod == M and N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
X = 10**200; K = (X - N0) // M
print("rows", len(rows), "ln M", math.log(M), "K = 2^%.2f" % math.log2(K), flush=True)
# primes to Z
t0 = time.time()
sv = np.ones(Z // 2, dtype=bool); sv[0] = False          # odd numbers 2i+1
for i in range(3, int(Z ** .5) + 1, 2):
    if sv[i // 2]: sv[i * i // 2::i] = False
P = (2 * np.nonzero(sv)[0] + 1).astype(np.int64); del sv
P = P[P > 463]
print("primes", len(P), time.time() - t0, flush=True)
gN0 = gmpy2.mpz(N0); gM = gmpy2.mpz(M)
a0 = np.fromiter((int(gN0 % int(x)) for x in P), dtype=np.int64, count=len(P))
b0 = np.fromiter((int(gM % int(x)) for x in P), dtype=np.int64, count=len(P))
print("residues", time.time() - t0, flush=True)
rowid = -np.ones(Q, dtype=np.int32); rowid[rows] = np.arange(len(rows))
nsmall = int(np.searchsorted(P, Q))
Ps = P[:nsmall]; reps = (Q + Ps - 1) // Ps
idx_rep = np.repeat(np.arange(nsmall), reps)
J = np.concatenate([np.arange(c) for c in reps]).astype(np.int64)
Prep = Ps[idx_rep]
Pb = P[nsmall:]; a0b = a0[nsmall:]; b0b = b0[nsmall:]
rng = np.random.default_rng(seed)
ks = np.sort(rng.choice(K, size=nmem, replace=False)).astype(np.int64)
LPF = np.zeros((nmem, len(rows)), dtype=np.int64)       # least prime factor found (0: survivor)
NF = np.zeros((nmem, len(rows)), dtype=np.int16)        # number of sieve primes dividing the row
PRP = np.zeros((nmem, len(rows)), dtype=np.int8)        # 1 if Fermat base 2 says probable prime (survivors only)
two = gmpy2.mpz(2); ntests = 0
for mi, k in enumerate(ks):
    k = int(k)
    res_s = (a0[:nsmall] + k * b0[:nsmall]) % Ps
    cand = res_s[idx_rep] + J * Prep
    ok = cand < Q; rid = rowid[cand[ok]]; pp = Prep[ok]; g = rid >= 0
    rid = rid[g]; pp = pp[g]
    res_b = (a0b + k * b0b) % Pb
    okb = res_b < Q; ridb = rowid[res_b[okb]]; ppb = Pb[okb]; gb = ridb >= 0
    rid = np.concatenate([rid, ridb[gb]]); pp = np.concatenate([pp, ppb[gb]])
    lpf = np.full(len(rows), np.iinfo(np.int64).max); np.minimum.at(lpf, rid, pp)
    lpf[lpf == np.iinfo(np.int64).max] = 0
    LPF[mi] = lpf; NF[mi] = np.bincount(rid, minlength=len(rows))
    N = gN0 + k * gM
    for j in np.nonzero(lpf == 0)[0]:
        n = N - int(rows[j])
        PRP[mi, j] = 1 if gmpy2.powmod(two, n - 1, n) == 1 else 0
        ntests += 1
    if mi % 50 == 0: print(mi, "members", ntests, "tests", "%.0f s" % (time.time() - t0), flush=True)
np.savez_compressed(out, ks=ks, LPF=LPF, NF=NF, PRP=PRP, rows=rows)
print("done", nmem, "members", ntests, "tests", int(PRP.sum()), "prp", time.time() - t0)

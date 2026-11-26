#!/usr/bin/env python3
"""Real 200-digit rows of the 200,000 cover: sieve to 10^6 (minus 25 'control' primes), Fermat-test every survivor.
Output ml_data.npz: per surviving row: member index, k, q, label (base-2 Fermat probable prime), ctrl (divisible by a control prime),
64 low bits and 64 high bits of n = N - q as bytes, residues modulo the odd primes below 100, a few Jacobi symbols."""
import sys, math, numpy as np, gmpy2, time
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
NM = int(sys.argv[1]) if len(sys.argv) > 1 else 600
Z = 10 ** 6; Q = 200000
rows, p0 = cr.load(cr.S + "q200000_m89.txt"); rows = rows[rows < Q]
line = [x for x in open(cr.S + "q200000_m89.txt") if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
M = 2 * math.prod(r for r, _ in cov)
# CRT, even
N0 = 0; P = 1
for r, a in [(2, 0)] + cov:
    t = ((a - N0) * pow(P, -1, r)) % r; N0 += P * t; P *= r
assert P == M and all(N0 % r == a for r, a in cov) and N0 % 2 == 0
K = (10 ** 200 - N0) // M
print("rows", len(rows), "ln M", math.log(M), "K", K, "log2 K", math.log2(K))
sv = np.ones(Z + 1, dtype=bool); sv[:2] = False
for i in range(2, int(Z ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
pr = np.nonzero(sv)[0]; pr = pr[pr > 463]
ctrl = pr[(pr > 1000)][:25]; print("control primes", ctrl[0], "to", ctrl[-1], "sum 1/p", (1 / ctrl).sum())
pr = np.setdiff1d(pr, ctrl)
N0p = np.array([N0 % int(p) for p in pr], dtype=np.int64); Mp = np.array([M % int(p) for p in pr], dtype=np.int64)
N0c = np.array([N0 % int(p) for p in ctrl], dtype=np.int64); Mc = np.array([M % int(p) for p in ctrl], dtype=np.int64)
small = pr <= Q
rowidx = -np.ones(Q + 1, dtype=np.int64); rowidx[rows] = np.arange(len(rows))
rng = np.random.default_rng(int(sys.argv[2]))
ks = np.sort(rng.choice(K, NM, replace=False))
sp = [p for p in range(3, 100) if all(p % d for d in range(2, p))]
out = {k: [] for k in ("mem", "k", "q", "y", "ctrl", "lo", "hi", "res", "jac", "S", "rank")}
t0 = time.time(); ntest = 0
for mi, k in enumerate(ks):
    k = int(k); c = (N0p + k * Mp) % pr                       # N mod p: p | N - q iff q = c mod p
    struck = np.zeros(Q + 1, dtype=bool)
    cs, ps = c[small], pr[small]
    cnt = (Q - cs) // ps + 1
    base = np.repeat(cs, cnt); step = np.repeat(ps, cnt)
    j = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    struck[base + step * j] = True
    cb = c[~small]; struck[cb[cb <= Q]] = True
    alive = rows[~struck[rows]]
    N = N0 + k * M
    cc = (N0c + k * Mc) % ctrl
    S = len(alive)
    for ri, q in enumerate(alive):
        q = int(q); n = N - q
        y = gmpy2.powmod(2, n - 1, n) == 1; ntest += 1
        out["mem"].append(mi); out["k"].append(k); out["q"].append(q); out["y"].append(bool(y))
        out["ctrl"].append(((q - cc) % ctrl == 0).any())
        out["lo"].append(n & (2 ** 64 - 1)); out["hi"].append(n >> (n.bit_length() - 64))
        out["res"].append([n % p for p in sp])
        out["jac"].append([gmpy2.jacobi(a, n) for a in (-1, 2, 3, 5, 7, q)])
        out["S"].append(S); out["rank"].append(ri)
    if mi % 50 == 0: print(mi, S, ntest, round(time.time() - t0, 1), flush=True)
y = np.array(out["y"]); ct = np.array(out["ctrl"])
print("rows", len(y), "primes", y.sum(), "rate", y.mean(), "ctrl-divisible", ct.sum(), "primes among them", (y & ct).sum())
np.savez_compressed(sys.argv[3], mem=np.array(out["mem"]), k=np.array(out["k"]), q=np.array(out["q"]), y=y, ctrl=ct,
                    lo=np.array(out["lo"], dtype=np.uint64), hi=np.array(out["hi"], dtype=np.uint64),
                    res=np.array(out["res"], dtype=np.int16), jac=np.array(out["jac"], dtype=np.int8), S=np.array(out["S"]), rank=np.array(out["rank"]), sp=np.array(sp))

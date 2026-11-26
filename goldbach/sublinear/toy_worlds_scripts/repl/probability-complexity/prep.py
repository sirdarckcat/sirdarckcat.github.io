#!/usr/bin/env python3
"""prep.py COVERFILE DEPTH OUTPREFIX [mod_r new_class]: write the per-prime data for wsieve.c
   rows: primes q < 200000 not in a cover class. members N0 + k M, k < K, N < 10^200."""
import sys, math, numpy as np, gmpy2
from sympy.ntheory.modular import crt
f, depth, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
Q = 200000
l = [x for x in open(f) if x.startswith(("COVER", "BEST"))][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
if len(sys.argv) > 5:
    r0, a0 = int(sys.argv[4]), int(sys.argv[5]); cov = [(r, (a0 if r == r0 else a)) for r, a in cov]
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PR = primes(Q - 1); PR = PR[PR > 2]
alive = np.ones(len(PR), dtype=bool)
for r, a in cov: alive &= (PR % r) != a
rows = PR[alive]
M = 2 * math.prod(r for r, _ in cov)
N0 = int(crt([2] + [r for r, _ in cov], [0] + [a for _, a in cov])[0])
X = 10 ** 200
K = (X - 1 - N0) // M + 1
big = primes(depth); rmax = max(r for r, _ in cov); big = big[big > rmax]
covset = set(r for r, _ in cov); big = np.array([p for p in big.tolist() if p not in covset] if rmax > 463 else big)
N0m = gmpy2.mpz(N0); Mm = gmpy2.mpz(M)
n0p = np.array([int(N0m % int(p)) for p in big], dtype=np.uint32)
mp = [int(Mm % int(p)) for p in big]
minv = np.array([pow(m, -1, int(p)) for m, p in zip(mp, big.tolist())], dtype=np.uint32)
with open(out + ".bin", "wb") as g:
    np.array([len(rows), len(big), K], dtype=np.uint64).tofile(g)
    rows.astype(np.uint32).tofile(g); big.astype(np.uint32).tofile(g); n0p.tofile(g); minv.tofile(g)
open(out + ".meta", "w").write(f"{len(rows)} {len(big)} {K} {N0} {M}\n")
print("rows", len(rows), "primes", len(big), "K", K, "log2 K", math.log2(K), "ln M", math.log(M))

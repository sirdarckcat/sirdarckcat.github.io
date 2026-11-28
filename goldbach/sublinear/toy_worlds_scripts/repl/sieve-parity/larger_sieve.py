#!/usr/bin/env python3
"""Gallagher's larger sieve on the real window: |Z| <= (sum ln s - ln K)/(sum ln s/nu_s - ln K) for a set Z of members lying in nu_s classes modulo s.
   For the best member of the whole window (first-order score on primes 463 < s <= 4600, from window_ls.py) take, with hindsight, at every prime the
   SMALLEST list of classes 'at least as heavy as the class the best member is in'. If even these lists have sum ln s/nu_s < ln K the larger sieve says nothing."""
import sys, math, numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
Q = 200000; S = 4600; kbest = int(sys.argv[1]) if len(sys.argv) > 1 else 18044336
f = cr.S + "q200000_m89.txt"
line = [x for x in open(f) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows, p = cr.load(f); rows = rows[rows < Q].astype(np.int64)
M = 2
for r, a in cov: M *= r
N0 = 0; mod = 1
for r, a in [(2, 0)] + cov:
    t = ((a - N0) * pow(mod, -1, r)) % r; N0 += mod * t; mod *= r
K = (10 ** 200 - N0) // M; N = N0 + kbest * M
sv = np.ones(S + 1, dtype=bool); sv[:2] = False
for i in range(2, int(S ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
PS = [int(s) for s in np.nonzero(sv)[0] if s > 463]
T = 0; sl = 0.0; sln = 0.0; zs = []; top5 = 0; above = 0; items = []
for s in PS:
    fs = np.bincount(rows % s, minlength=s); v = int(fs[N % s]); T += v
    nu = int((fs >= v).sum()); sl += math.log(s); sln += math.log(s) / nu; items.append((math.log(s) / nu, math.log(s), nu, s))
    zs.append((v - fs.mean()) / fs.std()); top5 += nu <= 0.05 * s; above += v > fs.mean()
zs = np.array(zs)
print(f"best member k = {kbest}: T = {T}; ln K = {math.log(K):.3f}")
print(f"its class is above the mean at {above} of {len(PS)} primes, in the heaviest 5% of classes at {top5}; mean z per prime {zs.mean():+.3f}, largest {zs.max():+.2f}")
print(f"hindsight lists (all classes at least as heavy as its own): sum ln s = {sl:.1f}, sum ln s/nu_s = {sln:.3f} against ln K = {math.log(K):.3f}: the larger sieve needs the second to exceed the third")
# best possible sub-collection of primes for the larger sieve: use only primes with small nu (hindsight), greedily
items.sort(reverse=True); acc = 0.0; accl = 0.0; best = None
for j, (w, l, nu, s) in enumerate(items):
    acc += w; accl += l
    if acc > math.log(K):
        b = (accl - math.log(K)) / (acc - math.log(K))
        if best is None or b < best[0]: best = (b, j + 1)
print("best sub-collection of primes (hindsight): " + (f"bound |Z| <= {best[0]:.1f} with {best[1]} primes" if best else f"none reaches ln K (largest attainable sum {acc:.3f})"))

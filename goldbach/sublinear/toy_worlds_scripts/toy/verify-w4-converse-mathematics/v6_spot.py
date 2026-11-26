#!/usr/bin/env python3
import math, numpy as np, sympy
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
line = [x for x in open(COVER) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows = np.array([q for q in sympy.primerange(3, Q) if all(q % r != a for r, a in cov)]); n = len(rows)
LP = list(sympy.primerange(467, 5000))
# quadratic signs free
g = 0.0
for s in LP:
    leg = np.array([sympy.legendre_symbol(int(c), s) if c else 0 for c in range(s)]); g += abs(int(leg[rows % s].sum())) / (s - 1)
print("free quadratic signs 467..5000: gain", round(g, 3), "rows over", len(LP), "primes")
# additive maxima
mx = []
for s in LP:
    t = np.bincount(rows % s, minlength=s).astype(float); P = np.abs(np.fft.fft(t)) ** 2 / (s * t.var()); mx.append(P[1:].max() / math.log(s - 1))
print("largest additive power / ln s: mean", round(float(np.mean(mx)), 3), "max", round(float(np.max(mx)), 2), "at", LP[int(np.argmax(mx))])
# progression lists, all d, all starts, s in [467,1000): densities 1/2 and 1/64 and lengths 1,2,3,4
rng = np.random.default_rng(0)
def best(t, Ls):
    s = len(t); d = np.arange(1, (s - 1) // 2 + 1); Lm = max(Ls)
    idx = (d[:, None] * np.arange(s + Lm)[None, :]) % s
    cs = np.zeros((len(d), s + Lm + 1), dtype=np.int64); np.cumsum(t[idx], axis=1, out=cs[:, 1:])
    return [(cs[:, L:L + s] - cs[:, :s]).max() / L - t.mean() for L in Ls]
res = []; resu = []
pr = [s for s in LP if s < 1000]
for s in pr:
    t = np.bincount(rows % s, minlength=s); Ls = [s // 2, max(2, s // 64), 1, 2, 3, 4, 6]
    res.append([(gv, gv / math.log(s / L)) for gv, L in zip(best(t, Ls), Ls)]); u = rng.permutation(t)
    resu.append([(gv, gv / math.log(s / L)) for gv, L in zip(best(u, Ls), Ls)])
res = np.array(res).mean(axis=0); resu = np.array(resu).mean(axis=0)
for name, r, u in zip(("1/2", "1/64", "L=1 (pin)", "L=2", "L=3", "L=4", "L=6"), res, resu):
    print(f"   [467,1000) {name:10s}: gain real {r[0]:.4f} shuffled {u[0]:.4f}; rate real {r[1]:.4f} shuffled {u[1]:.4f} rows/nat")

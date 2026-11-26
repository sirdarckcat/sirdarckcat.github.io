#!/usr/bin/env python3
"""Independent recomputation of the whole-window tail (t9) and of the sum-closure test (t7b)."""
import math, numpy as np, sympy
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
line = [x for x in open(COVER) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows = np.array([q for q in sympy.primerange(3, Q) if all(q % r != a for r, a in cov)])
from sympy.ntheory.modular import crt
M = 2 * math.prod(r for r, a in cov); N0 = int(crt([2] + [r for r, a in cov], [0] + [a for r, a in cov])[0]); K = (10 ** 200 - 1 - N0) // M + 1
LQ = list(sympy.primerange(467, 2000)); T = [np.bincount(rows % s, minlength=s).astype(np.int16) for s in LQ]
S = np.zeros(K, dtype=np.int16); k = np.arange(K, dtype=np.int64)
for s, t in zip(LQ, T):
    S += t[(N0 % s + k * (M % s)) % s]
# exact product model by direct convolution of the value distributions
pmf = np.array([1.0])
for t in T: pmf = np.convolve(pmf, np.bincount(t) / len(t))
tail = np.cumsum(pmf[::-1])[::-1]
print("K", K, "primes", len(LQ), "mean", S.mean(), "var", S.astype(np.float64).var(), "product var", sum(t.astype(float).var() for t in T), "max", S.max())
for x in (331, 348, 361, 372, 381, 389, 395, 397):
    print(f"  S >= {x}: observed {(S >= x).sum()}  expected {K * tail[x]:.1f}")
# sum closure on the first 2^21 (k1+k2 < 2^22)
H = 1 << 21; S1 = S[:H]; thr = np.quantile(S1, 0.99); top = np.nonzero(S1 >= thr)[0]; rng = np.random.default_rng(123)
i1 = rng.choice(top, 400000); i2 = rng.choice(top, 400000); ss = S[i1 + i2].astype(float)
print(f"top 1%: {len(top)} members mean {S1[top].mean():.2f}; S(k1+k2): {ss.mean():.3f} +- {ss.std()/math.sqrt(len(ss)):.3f}; all {S.mean():.3f}; S(k1+k2+1) control: {S[i1+i2+1].mean():.3f}")
# does a sum of top members share residues? S(k1+k2) should be correlated with S(k1) only through f_s(x+y): none expected

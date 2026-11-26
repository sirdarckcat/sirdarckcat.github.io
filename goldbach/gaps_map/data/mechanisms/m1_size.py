# M1: size-aware ranking (k1, 1/ln N, k1/ln N); fit on one miniature, test on the others; baseline = cover first (order by k1).
import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
NB = 24; XS = {'A': 10**9, 'B': 2 * 10**9, 'C': 10**9}
D = {}
for nm in 'ABC':
    m = Mini(nm); X = XS[nm]
    kf = lambda a, b: np.asarray(m.k[a:b, 0]).astype(np.int64) * NB + np.minimum((m.idx[a:b].astype(np.int64) * 2 * NB) // X, NB - 1)
    c, sc, sk = keyed_counts(m, kf, 60 * NB); D[nm] = (c, sc, sk, X)
kk = np.arange(60 * NB) // NB; ub = (np.arange(60 * NB) % NB + 0.5) / NB
def design(X):
    lnN = np.log(np.maximum(ub * X, 10.0)); return np.stack([np.ones_like(lnN), kk.astype(float), 1000 / lnN, kk / lnN * 100], axis=1)
print('M1 size/posterior ranking: sigma = -(fitted logit on k1, 1/lnN, k1/lnN); baseline sigma = k1')
for tr in 'ABC':
    c, sc, sk, X = D[tr]; msk = c > 0
    beta = fit_logit(design(X)[msk], c[msk].astype(float), sc[msk].astype(float))
    for te in 'ABC':
        c2, sc2, sk2, X2 = D[te]; sig = -(design(X2) @ beta)
        pt, bs, pb, pm = gain_boot(c2, sc2, sk2, kk.astype(float), sig, B=200)
        print(f' fit {tr} -> test {te}:', fmt(pt, bs), flush=True)

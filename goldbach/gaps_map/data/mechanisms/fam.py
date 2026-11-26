import numpy as np, sys, math, subprocess, os
sys.path.insert(0, '.')
from lib import *
X, Q = 10**9, 1000
m = Mini('A'); rho1 = 0.5
def pw(k): return np.power(1.0 - rho1, k.astype(np.float64))
# ---- population baseline: per-k1 mean predicted success mass, and calibration constant
K1 = 64; sumP = np.zeros(K1); cnt = np.zeros(K1, dtype=np.int64); obs = np.zeros(K1)
for a in range(0, m.M, CH):
    b = min(a + CH, m.M); kk = np.asarray(m.k[a:b]); k1 = kk[:, 0].astype(np.int64)
    sumP += np.bincount(k1, weights=pw(kk[:, 5]), minlength=K1); cnt += np.bincount(k1, minlength=K1)
    obs += np.bincount(k1, weights=np.asarray(m.s[a:b]), minlength=K1)
cal = obs.sum() / sumP.sum(); mu = np.where(cnt > 0, sumP / np.maximum(cnt, 1), 0.0)
print('calibration constant c = observed/predicted =', round(cal, 3), '; predicted by k1 vs observed:')
for v in range(26, 42, 2): print(' k1', v, 'members', cnt[v], 'pred', round(cal * sumP[v], 1), 'obs', int(obs[v]))
np.savez('pop_A.npz', mu=mu, cnt=cnt, cal=cal, sumP=sumP, obs=obs)

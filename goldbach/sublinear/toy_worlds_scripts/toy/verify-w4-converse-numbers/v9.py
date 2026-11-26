# whole window score over 213 primes 467..1999; saves S as int16
import math, numpy as np
from vlib import *
cov, rows = get(); N0, M, K = win(cov)
P = lp(467, 2000); print(len(P), "primes", K)
S = np.zeros(K, dtype=np.int16)
pm = np.array([1.0])
for s in P:
    t = tab(rows, s)
    # residue of member k: (N0 + k M) mod s -> periodic pattern of length s in k
    pat = t[(N0 % s + (M % s) * np.arange(s)) % s].astype(np.int16)
    reps = K // s + 1
    S += np.tile(pat, reps)[:K]
    pm = np.convolve(pm, np.bincount(t) / s)
np.save("S_all.npy", S)
x = np.arange(len(pm)); mean = (pm * x).sum(); var = (pm * x * x).sum() - mean ** 2
Sf = S.astype(np.float64)
print("mean %.4f (product %.4f) var %.3f (product %.3f) ratio %.5f" % (Sf.mean(), mean, Sf.var(), var, Sf.var() / var))
hist = np.bincount(S, minlength=len(pm)); obs = np.cumsum(hist[::-1])[::-1]; tail = np.cumsum(pm[::-1])[::-1]
for thr in (331, 348, 361, 372, 381, 389, 397):
    e = K * tail[thr]; print("S>=%d obs %d exp %.1f ratio %.4f +- %.4f" % (thr, obs[thr], e, obs[thr] / e, 1 / math.sqrt(e)))
print("max S", S.max(), "expected at or above", K * tail[S.max()])
# lower tail too (adversarial: page only checked upper tail)
low = np.cumsum(hist); ltail = np.cumsum(pm)
for q in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
    i = int(np.argmax(ltail > q)) - 1; e = K * ltail[i]; print("S<=%d obs %d exp %.1f ratio %.4f +- %.4f" % (i, low[i], e, low[i] / e, 1 / math.sqrt(e)))
# first 2^22
KK = 1 << 22; h2 = np.bincount(S[:KK], minlength=len(pm)); o2 = np.cumsum(h2[::-1])[::-1]
print("first 2^22: var", S[:KK].astype(float).var(), "S>=381:", o2[381], KK * tail[381], "S>=389:", o2[389], KK * tail[389], "max", S[:KK].max())

#!/usr/bin/env python3
"""t7: correlations between the tables of different primes, and closure under sums.
 (a) through the window: members N0 + k M, k < 2^22 (the first 2^22 of the real window), primes 467..2000:
     x_s(k) = f_s((N0 + k M) mod s).  Pair correlations of x_s, x_s' over k (independent draws: z = corr sqrt(2^22) ~ N(0,1));
     variance of S = sum_s x_s against the sum of the variances.
 (b) sums: N(k1) + N(k2) - N0 = N(k1 + k2) is again a member.  Is the sum of two good members good?  Top 1% of S among
     k < 2^21: mean S(k1 + k2) over random pairs of top members, against the mean of all members.
 (c) common-integer labelling: corr over c < s of f_s(c) and f_s'(c) (s < s'), pairs of primes in three ranges; the only
     shared row of the classes c mod s and c mod s' is c itself (s s' > Q), so the predicted covariance is
     (1/s) #{rows < s} (1 - mean terms)."""
import math, numpy as np
from common import *
cov, rows = load(); n = len(rows); N0, M, K = window(cov)
LP = later_primes(464, 2000); m = len(LP); T = [table(rows, s).astype(np.float32) for s in LP]
a0 = [N0 % s for s in LP]; dm = [M % s for s in LP]
KK = 1 << 22; CH = 1 << 16
G2 = np.zeros((m, m)); G1 = np.zeros(m); S_all = np.zeros(KK, dtype=np.float32)
for c0 in range(0, KK, CH):
    k = np.arange(c0, c0 + CH, dtype=np.int64); X = np.empty((CH, m), dtype=np.float32)
    for i, s in enumerate(LP): X[:, i] = T[i][(a0[i] + k * dm[i]) % s]
    G1 += X.sum(axis=0, dtype=np.float64); G2 += (X.T.astype(np.float64) @ X.astype(np.float64)); S_all[c0:c0 + CH] = X.sum(axis=1)
mu = G1 / KK; C = G2 / KK - np.outer(mu, mu); sd = np.sqrt(np.diag(C)); R = C / np.outer(sd, sd); iu = np.triu_indices(m, 1); z = R[iu] * math.sqrt(KK)
tv = np.array([t.var() for t in T]); tm = np.array([t.mean() for t in T])
print(f"(a) {m} primes 467..1999, {KK} members of the real window: pairs {len(z)}")
print(f"    z = corr sqrt(members): mean {z.mean():+.4f}, rms {math.sqrt((z**2).mean()):.4f} (independent: 1), largest |z| {np.abs(z).max():.2f} (expected about {math.sqrt(2*math.log(len(z))):.2f}); |z| > 3: {(np.abs(z) > 3).sum()} (expected {len(z)*0.0027:.0f})")
print(f"    mean over the window against mean of the table: largest |difference|/sd(table) sqrt(members) = {np.abs((mu - tm) / np.sqrt(tv) * math.sqrt(KK)).max():.2f};  variance over the window / variance of the table: mean {np.mean(np.diag(C)/tv):.5f}")
print(f"    Var(S) over the window {S_all.var():.3f}; sum of table variances {tv.sum():.3f}; ratio {S_all.var()/tv.sum():.5f} (sampling sd about {math.sqrt(2/KK)*3:.5f})")
H = 1 << 21; S1 = S_all[:H]; thr = np.quantile(S1, 0.99); top = np.nonzero(S1 >= thr)[0]; rng = np.random.default_rng(5)
i1 = rng.choice(top, 400000); i2 = rng.choice(top, 400000); ss = S_all[i1 + i2]; ok = i1 != i2
print(f"(b) top 1% of S among k < 2^21: {len(top)} members, mean S {S1[top].mean():.2f} against {S_all.mean():.2f} for all (sd {S_all.std():.2f})")
print(f"    S(k1 + k2) over {ok.sum()} pairs of top members: mean {ss[ok].mean():.3f}, sd of that mean {ss[ok].std()/math.sqrt(ok.sum()):.3f}; all members {S_all.mean():.3f}: excess {(ss[ok].mean()-S_all.mean()):+.3f} rows")
i3 = rng.choice(top, 400000); k3 = 2 * i3; print(f"    S(2 k1) over top members: mean {S_all[k3].mean():.3f} (excess {S_all[k3].mean()-S_all.mean():+.3f}, sd of mean {S_all[k3].std()/math.sqrt(len(top)):.3f})")
print("(c) common-integer labelling")
AP = primes_upto(60000)
for lo, hi, cnt in ((467, 1000, 78), (2000, 5000, 120), (20000, 60000, 120)):
    pr = [int(x) for x in AP[(AP >= lo) & (AP < hi)]]; step = max(1, len(pr) // cnt); pr = pr[::step]; tabs = {s: table(rows, s).astype(float) for s in pr}
    cs = []; pred = []
    for i, s in enumerate(pr):
        for s2 in pr[i + 1:]:
            a = tabs[s]; b = tabs[s2][:s]; cs.append(np.corrcoef(a, b)[0, 1]); pred.append(((rows < s).sum() / s) / math.sqrt(a.var() * b.var()))
    cs = np.array(cs); print(f"    primes in [{lo},{hi}): {len(pr)} primes, {len(cs)} pairs: mean corr {cs.mean():+.5f} +- {cs.std()/math.sqrt(len(cs)):.5f}; predicted from the shared row c {np.mean(pred):+.5f}")

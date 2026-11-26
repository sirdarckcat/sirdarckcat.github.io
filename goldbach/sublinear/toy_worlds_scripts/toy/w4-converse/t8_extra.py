#!/usr/bin/env python3
"""t8: three complements.
 (a) additive energy of the heavy list of each table (classes with at least the upper-quartile count, and at least one row),
     E(A) = #{a+b = c+d in A}, against random sets of the same size: relative excess, by range of primes; and the share of the
     table's variance carried by the largest additive coefficient.
 (b) pair correlations through a window shorter than every product s s' (2^17 members; 467*479 = 223,693).
 (c) is the window a fair sample of the product in the tail?  Histogram of S (primes 467..1999) over 2^22 members of the real
     window against the exact convolution of the 213 tables (independent uniform residues)."""
import math, numpy as np
from common import *
cov, rows = load(); n = len(rows); N0, M, K = window(cov); rng = np.random.default_rng(9)
print("(a) additive energy of the heavy list and the largest additive coefficient")
LP = later_primes(464, 5000); rec = []
for s in LP:
    t = table(rows, s).astype(float); thr = np.sort(t)[::-1][max(1, s // 4) - 1]; A = (t >= max(thr, 1)).astype(float); a = A.sum()
    F = np.abs(np.fft.fft(A)) ** 2; E = float((F ** 2).sum()) / s                       # all quadruples a+b=c+d
    Er = np.mean([float((np.abs(np.fft.fft(rng.permutation(A))) ** 2 ** 1).__pow__(2).sum()) / s for _ in range(6)])
    P = np.abs(np.fft.fft(t)) ** 2; share = P[1:].max() * 2 / P[1:].sum()                # h and -h
    Pu = np.abs(np.fft.fft(rng.permutation(t))) ** 2; shu = Pu[1:].max() * 2 / Pu[1:].sum()
    rec.append((s, a / s, E / Er - 1, (a ** 3 * 2 / 3) / Er - 1, share, shu))
rec = np.array(rec)
for lo, hi in ((467, 1000), (1000, 2000), (2000, 3500), (3500, 5000)):
    k = (rec[:, 0] >= lo) & (rec[:, 0] < hi); r = rec[k]
    print(f"    s in [{lo},{hi}): density {r[:,1].mean():.2f}; energy / random - 1: {r[:,2].mean():+.5f} +- {r[:,2].std()/math.sqrt(k.sum()):.5f}  (an interval of that size would give {r[:,3].mean():+.2f});"
          f"  share of variance in the largest coefficient: real {r[:,4].mean():.4f}, shuffled {r[:,5].mean():.4f}")

LQ = later_primes(464, 2000); m = len(LQ); T = [table(rows, s).astype(np.float32) for s in LQ]; a0 = [N0 % s for s in LQ]; dm = [M % s for s in LQ]
def block(k0, cnt):
    k = np.arange(k0, k0 + cnt, dtype=np.int64); X = np.empty((cnt, m), dtype=np.float32)
    for i, s in enumerate(LQ): X[:, i] = T[i][(a0[i] + k * dm[i]) % s]
    return X
print("(b) pair correlations, 16 windows of 2^17 consecutive members of the real window, primes 467..1999")
zs = []
for w in range(16):
    X = block(w * (1 << 20), 1 << 17).astype(np.float64); R = np.corrcoef(X.T); iu = np.triu_indices(m, 1); zs.append(R[iu] * math.sqrt(1 << 17))
zs = np.array(zs); print(f"    z = corr sqrt(members): rms {math.sqrt((zs**2).mean()):.4f} (independent draws: 1), largest |z| {np.abs(zs).max():.2f} of {zs.size} (expected about {math.sqrt(2*math.log(zs.size)):.2f}); |z| > 3: {(np.abs(zs)>3).sum()} (expected {zs.size*0.0027:.0f})")
print("(c) tail of S over 2^22 members against the convolution of the tables")
KK = 1 << 22; S = np.zeros(KK, dtype=np.int32)
for c0 in range(0, KK, 1 << 16): S[c0:c0 + (1 << 16)] = block(c0, 1 << 16).sum(axis=1).astype(np.int32)
pmf = np.array([1.0])
for t in T: pmf = np.convolve(pmf, np.bincount(t.astype(int)) / len(t))
tail = np.cumsum(pmf[::-1])[::-1]; hist = np.bincount(S, minlength=len(pmf)); obs = np.cumsum(hist[::-1])[::-1]
print(f"    mean {S.mean():.3f} (product: {np.dot(np.arange(len(pmf)), pmf):.3f}); sd {S.std():.3f} (product: {math.sqrt(np.dot(np.arange(len(pmf))**2, pmf) - np.dot(np.arange(len(pmf)), pmf)**2):.3f})")
for q in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
    x = int(np.argmax(tail <= q)); e = KK * tail[x]; print(f"    S >= {x}: expected {e:10.1f}, observed {int(obs[x]):8d}, ratio {obs[x]/e:.4f} +- {1/math.sqrt(e):.4f}")
print(f"    largest S in the window: {S.max()}; expected number at or above it {KK*tail[S.max()]:.2f}")

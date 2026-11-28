#!/usr/bin/env python3
"""t9: the whole real window (all K = 21,378,978 members below 10^200 of the 200,000 cover): first-order score over the
213 primes 467..1999, S(k) = sum_s f_s((N0 + k M) mod s), against the exact convolution of the tables (the random box)."""
import math, numpy as np
from common import *
cov, rows = load(); N0, M, K = window(cov)
LQ = later_primes(464, 2000); m = len(LQ); T = [table(rows, s).astype(np.int32) for s in LQ]; a0 = [N0 % s for s in LQ]; dm = [M % s for s in LQ]
pmf = np.array([1.0])
for t in T: pmf = np.convolve(pmf, np.bincount(t) / len(t))
hist = np.zeros(len(pmf), dtype=np.int64); CH = 1 << 18
for c0 in range(0, K, CH):
    k = np.arange(c0, min(K, c0 + CH), dtype=np.int64); S = np.zeros(len(k), dtype=np.int32)
    for i, s in enumerate(LQ): S += T[i][(a0[i] + k * dm[i]) % s]
    hist += np.bincount(S, minlength=len(pmf))
tail = np.cumsum(pmf[::-1])[::-1]; obs = np.cumsum(hist[::-1])[::-1]; x = np.arange(len(pmf))
mean = (hist * x).sum() / K; var = (hist * x * x).sum() / K - mean ** 2; pm = (pmf * x).sum(); pv = (pmf * x * x).sum() - pm ** 2
print(f"members {K}; mean {mean:.4f} (product {pm:.4f}); variance {var:.3f} (product {pv:.3f}), ratio {var/pv:.5f}")
for q in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7):
    i = int(np.argmax(tail <= q)); e = K * tail[i]; print(f"  S >= {i}: expected {e:11.1f}, observed {int(obs[i]):9d}, ratio {obs[i]/e:.4f} +- {1/math.sqrt(e):.4f}")
top = int(np.nonzero(hist)[0].max()); print(f"  largest S: {top}; expected number at or above it {K*tail[top]:.2f}")

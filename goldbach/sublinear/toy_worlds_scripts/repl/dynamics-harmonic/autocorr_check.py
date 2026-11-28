#!/usr/bin/env python3
"""Check of the autocorrelation law: Cov(S(k), S(k+T)) to first order = sum over later primes r of
W^2 (1-1/r)^-2 A_r(T M mod r),  A_r(s) = (1/r) sum_c g_r(c) g_r(c+s),  g_r = (rows per class of r) - n/r.
Measured on the whole real window at depth 1e8 against the tables (primes to 30000), for 400 lags."""
import math, numpy as np
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows)
S = np.fromfile("S_100000000.u16", dtype=np.uint16).astype(np.float64); mu = S.mean(); var = S.var(); x = S - mu; W = mu / n
sv = np.ones(30001, bool); sv[:2] = False
for i in range(2, 174):
    if sv[i]: sv[i * i::i] = False
P = [int(p) for p in np.nonzero(sv)[0] if p >= 467]
rng = np.random.default_rng(3); lags = [1, 2, 6, 30, 210, 2310, 30030, 510510, 9699690, 467, 479, 487, 934, 467 * 479, 963748, 1133229] + [int(t) for t in rng.integers(1, K // 2, 384)]
tabs = []
for r in P:
    f = np.bincount(rows % r, minlength=r).astype(float); g = f - n / r; G = np.fft.rfft(g); A = np.fft.irfft(G * np.conj(G), r) / r    # A[s] = (1/r) sum g(c) g(c+s)
    tabs.append((r, M % r, W ** 2 / (1 - 1 / r) ** 2 * A))
pred = []; meas = []
for T in lags:
    p = sum(A[(T * m) % r] for r, m, A in tabs); pred.append(p / var); meas.append(float(np.dot(x[:-T], x[T:]) / (K - T) / var))
pred = np.array(pred); meas = np.array(meas)
for i in range(16): print(f"lag {lags[i]}: measured {meas[i]:+.6f}  tables {pred[i]:+.6f}")
g = slice(16, None); c = np.corrcoef(pred[g], meas[g])[0, 1]; res = meas[g] - pred[g]
print(f"384 random lags: sd measured {meas[g].std():.6f}, sd predicted {pred[g].std():.6f}, correlation {c:.4f}, sd of residual {res.std():.6f} (sampling noise 1/sqrt(K) = {1/math.sqrt(K):.6f}), mean measured {meas[g].mean():+.6f}, mean predicted {pred[g].mean():+.6f}")
print(f"largest |measured| over the random lags {np.abs(meas[g]).max():.6f}")

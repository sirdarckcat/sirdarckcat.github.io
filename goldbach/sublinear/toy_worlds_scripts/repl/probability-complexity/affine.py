#!/usr/bin/env python3
"""affine.py: non-translation maps of the window (k -> a k + b, reflection): correlation of exact sieve counts, depth 10^8."""
import numpy as np, math
S = np.fromfile("S8.100000000.u16", dtype=np.uint16).astype(np.float64); K = len(S); Z = (S - S.mean()) / S.std()
k = np.arange(K)
def rep(name, i, j):
    c = float((Z[i] * Z[j]).mean()); print(f"{name}: corr {c:+.5f} +- {1/math.sqrt(len(i)):.5f}")
h = np.arange(K // 2); rep("k -> 2k", h, 2 * h)
t = np.arange(K // 3 - 1); rep("k -> 3k+1", t, 3 * t + 1)
rep("k -> K-1-k (reflection)", k[:K // 2], K - 1 - k[:K // 2])
q = np.arange(1, 4600); rep("k -> k^2 (k < 4600)", q, q * q)
a = 467 * 479; m = np.arange(K - 1); rep("k -> k xor 1", m[::2], m[::2] + 1)
i = np.arange(K - a - 5); rep("k -> k + 467*479 (reference)", i, i + a)

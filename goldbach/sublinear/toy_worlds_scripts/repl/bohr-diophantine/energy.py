#!/usr/bin/env python3
"""(c) Additive structure of the best members of the real window by exact sieve count (to 10^8).
A = the members with S <= t (about 1%, 0.1%, 0.01%).  Exact integer statistics by FFT (length 2^26 >= 2K, no wrap):
  r(d) = #{(a, b) in A^2 : a - b = d},  E(A) = sum_d r(d)^2  (additive energy),
  uniformity: max over the FFT grid of |sum_{k in A} e(k xi) - tau sum_{k<K} e(k xi)| / |A|
against uniformly random subsets of [0, K) of the same size (same code)."""
import sys, math, time, numpy as np
from base import *
S = np.fromfile("S_100000000.u16", dtype=np.uint16); assert len(S) == K
NF = 1 << 26
def stats(mask):
    n = int(mask.sum()); tau = n / K
    x = np.zeros(NF, dtype=np.float64); x[:K] = mask
    F = np.fft.rfft(x); del x
    P = F.real ** 2 + F.imag ** 2
    r = np.fft.irfft(P, NF); del P
    r = np.rint(r)                       # r[d] for d >= 0 at index d, d < 0 at NF + d
    E = float((r * r).sum())
    # balanced function for uniformity: subtract tau * interval transform
    y = np.zeros(NF, dtype=np.float64); y[:K] = tau
    F -= np.fft.rfft(y); del y
    mag = np.abs(F); j = int(np.argmax(mag)); mx = float(mag[j]) / n
    return n, E, mx, j / NF, r
def report(name, t, nrand, rng):
    mask = S <= t
    n, E, mx, xi, r = stats(mask)
    # E for a uniformly random n-subset: measured
    Er = []; mr = []
    for _ in range(nrand):
        idx = rng.choice(K, size=n, replace=False); m2 = np.zeros(K, dtype=bool); m2[idx] = True
        n2, E2, mx2, _, _ = stats(m2); Er.append(E2); mr.append(mx2)
    Er = np.array(Er); mr = np.array(mr)
    triv = 2.0 * n * n - n                                  # a=b,c=d and a=c,b=d
    print(f"{name}: S <= {t}: |A| = {n} ({100 * n / K:.4f}% of K)")
    print(f"  energy E(A) = {E:.6e}; random sets of the same size ({nrand}): mean {Er.mean():.6e} sd {Er.std(ddof=1):.3e}; ratio {E / Er.mean():.7f}; excess {(E - Er.mean()) / Er.std(ddof=1):+.1f} sd")
    print(f"  E/|A|^3 = {E / n ** 3:.5f} (1 for a progression of the same size x 2/3; random prediction 2|A|/(3K)+2/|A| = {2 * n / (3 * K) + 2 / n:.5f}); nontrivial quadruples/|A|^3 = {(E - triv) / n ** 3:.5f}")
    print(f"  largest Fourier coefficient of the balanced indicator / |A|: {mx:.5f} at xi = {xi:.6f}; random sets: mean {mr.mean():.5f} max {mr.max():.5f}; 1/sqrt|A| = {1 / math.sqrt(n):.5f}")
    # differences that are multiples of a later prime: r(d) against the smooth expectation n^2 (K-d)/K^2
    for s in (467, 479, 487, 1009, 468, 500):
        d = np.arange(s, K // 2, s); rr = r[d]; exp_ = n * (n - 1.0) * (K - d) / (K * (K - 1.0))
        print(f"    differences d = multiples of {s} below K/2: sum r(d) / expected = {rr.sum() / exp_.sum():.5f} (sd of the ratio for a random set {1 / math.sqrt(exp_.sum()):.5f})")
    return mask
if __name__ == "__main__":
    rng = np.random.default_rng(11)
    h = np.bincount(S); c = np.cumsum(h)
    print(f"exact sieve to 10^8 of the real window: K = {K}, mean {S.mean():.3f}, sd {S.std():.3f}, min {S.min()}")
    for frac, nr in ((0.01, 6), (0.001, 6), (0.0001, 6)):
        t = int(np.searchsorted(c, frac * K)); 
        if abs(c[t - 1] - frac * K) < abs(c[t] - frac * K): t -= 1
        report(f"top {100 * frac:g}%", t, nr, rng)

#!/usr/bin/env python3
"""(c) continued.  (1) U^2 statistic free of the large-scale shape: f = 1_A - tau 1_[0,K);
Q = mean over frequencies |xi| >= 0.001 of |f^(xi)|^4 / (2 (|A|(1-tau))^2)   (1 for a random set; the excess is the
additive structure of A beyond its size), with the largest peaks identified as fractions a/s.
(2) the top 0.01% and 0.001% by direct count of differences against 200 random sets."""
import math, numpy as np, gc
from fractions import Fraction
from base import *
S = np.fromfile("S_100000000.u16", dtype=np.uint16); NF = 1 << 26
def q_stat(mask, peaks=0):
    n = int(mask.sum()); tau = n / K
    x = np.full(NF, 0.0); x[:K] = mask; x[:K] -= tau
    F = np.fft.rfft(x); del x; gc.collect()
    p = F.real ** 2 + F.imag ** 2; del F; gc.collect()
    lo = int(0.001 * NF); sig2 = n * (1 - tau)
    Q = float((p[lo:] ** 2).mean() / (2 * sig2 * sig2)); m2 = float(p[lo:].mean() / sig2)
    out = []
    if peaks:
        idx = np.argpartition(p[lo:], -4000)[-4000:] + lo; idx = idx[np.argsort(-p[idx])]
        seen = []
        for j in idx:
            xi = j / NF
            fr = Fraction(xi).limit_denominator(3000)
            if abs(float(fr) - xi) > 2.0 / K: fr = None
            if fr is not None and any(fr == g for g, _ in seen): continue
            if fr is None and any(g is None and abs(x0 - xi) < 3 / K for g, (x0) in seen): continue
            seen.append((fr, xi)); out.append((math.sqrt(p[j]) / n, xi, fr))
            if len(out) >= peaks: break
    del p; gc.collect()
    return n, Q, m2, out
rng = np.random.default_rng(23)
h = np.bincount(S); c = np.cumsum(h)
for frac in (0.01, 0.001):
    t = int(np.searchsorted(c, frac * K))
    if abs(c[t - 1] - frac * K) < abs(c[t] - frac * K): t -= 1
    mask = S <= t; n, Q, m2, pk = q_stat(mask, 12)
    Qr = []
    for _ in range(4):
        idx = rng.choice(K, size=n, replace=False); m = np.zeros(K, dtype=bool); m[idx] = True
        Qr.append(q_stat(m)[1]); del m
    Qr = np.array(Qr)
    print(f"S <= {t}: |A| = {n}; Q = {Q:.5f}; mean |f^|^2 / (|A|(1-tau)) = {m2:.5f}; random sets (4): Q = {Qr.mean():.5f} +- {Qr.std(ddof=1):.5f}; excess of fourth moment {Q - Qr.mean():+.5f} = {(Q - Qr.mean()) / Qr.std(ddof=1):+.1f} sd", flush=True)
    print("   largest coefficients |f^|/|A| and their frequencies (fraction a/s with s <= 3000 when within 2/K):")
    for a, xi, fr in pk: print(f"      {a:.5f}  xi = {xi:.7f}  {fr if fr is not None else 'no small denominator'}")
def energy_direct(pos):
    d = (pos[:, None] - pos[None, :]).ravel(); u, cnt = np.unique(d, return_counts=True)
    return float((cnt.astype(np.float64) ** 2).sum())
for frac in (0.0001, 0.00001):
    t = int(np.searchsorted(c, frac * K))
    if abs(c[t - 1] - frac * K) < abs(c[t] - frac * K): t -= 1
    pos = np.nonzero(S <= t)[0].astype(np.int64); n = len(pos); E = energy_direct(pos)
    Er = np.array([energy_direct(np.sort(rng.choice(K, size=n, replace=False)).astype(np.int64)) for _ in range(200 if n < 3000 else 40)])
    triv = 2.0 * n * n - n
    print(f"S <= {t}: |A| = {n}; E = {E:.0f}; trivial quadruples 2|A|^2-|A| = {triv:.0f}; nontrivial {E - triv:.0f}; random sets ({len(Er)}): nontrivial mean {Er.mean() - triv:.0f} sd {Er.std(ddof=1):.0f}; excess {(E - Er.mean()) / Er.std(ddof=1):+.2f} sd; E/|A|^3 = {E / n ** 3:.5f}")

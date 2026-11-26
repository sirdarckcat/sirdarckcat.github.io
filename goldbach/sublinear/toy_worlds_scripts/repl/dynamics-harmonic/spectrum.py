#!/usr/bin/env python3
"""(a)+(b), part 2: spectrum, autocorrelation at every lag, and interval (block) hierarchy of the exact sieve count on the
real window.   python3 spectrum.py <depth>"""
import sys, math, numpy as np
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows); z = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10 ** 5
S = np.fromfile(f"S_{z}.u16", dtype=np.uint16).astype(np.float64); mu = S.mean(); var = S.var(); x = S - mu
print(f"depth {z}: mean {mu:.3f} var {var:.3f}")
# ---- D. periodogram on the first 2^24 members
L = 1 << 24; xs = x[:L] - x[:L].mean(); F = np.fft.rfft(xs); Pw = (F.real ** 2 + F.imag ** 2); Pw = Pw[1:L // 2]   # bins 1..L/2-1
tot = Pw.sum(); nb = len(Pw); order = np.argsort(Pw)[::-1]; cs = np.cumsum(Pw[order]) / tot
rng = np.random.default_rng(5); xp = rng.permutation(xs); Fp = np.fft.rfft(xp); Pp = (Fp.real ** 2 + Fp.imag ** 2)[1:L // 2]; Pp.sort(); Pp = Pp[::-1]; csp = np.cumsum(Pp) / Pp.sum()
print(f"periodogram of the first 2^24 members: {nb} bins; mean bin power = 1 unit")
print("top m bins | share of variance | same for a random permutation of the same values | white-noise formula p(1-ln p)")
for m in (1, 10, 100, 1000, 10 ** 4, 10 ** 5, 10 ** 6):
    p = m / nb; print(f"  {m} | {cs[m-1]:.6f} | {csp[m-1]:.6f} | {p*(1-math.log(p)):.6f}")
mean = tot / nb; print(f"largest bin: {Pw[order[0]]/mean:.1f} units; permuted data: {Pp[0]/(Pp.sum()/nb):.1f}; bins above the permuted maximum: {(Pw > Pp[0]*tot/Pp.sum()).sum()} carrying {Pw[Pw > Pp[0]*tot/Pp.sum()].sum()/tot:.5f} of the variance")
# identify the top bins with fractions t/r, r a later prime
def primes(a, b):
    sv = np.ones(b + 1, bool); sv[:2] = False
    for i in range(2, int(b ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    p = np.nonzero(sv)[0]; return p[p >= a]
P = primes(467, 3000); top = order[:2000] + 1; ident = np.zeros(len(top), dtype=np.int64)
for r in P:
    fr = top * int(r) / L; d = np.abs(fr - np.round(fr)); ident[(d < 1.0 * r / L * 1.0) & (ident == 0)] = r      # within one bin of t/r
big = (Pw > Pp[0] * tot / Pp.sum()); idx = np.nonzero(big)[0] + 1; idr = np.zeros(len(idx), dtype=np.int64)
for r in P:
    fr = idx * int(r) / L; d = np.abs(fr - np.round(fr)); idr[(d < 1.0 * r / L) & (idr == 0)] = r
print(f"of the {len(idx)} bins above the permuted maximum, {int((idr > 0).sum())} lie within one bin of t/r for a prime 467 <= r < 3000; largest r among them {idr.max()}; chance rate for a random bin: {sum(2.0*(r-1)/ (L/2) for r in P):.4f}")
print("top 12 bins: bin, power (units), nearest later prime r with t/r within a bin:", [(int(top[i]), round(float(Pw[order[i]] / mean), 1), int(ident[i])) for i in range(12)])
# in-sample oracle reconstruction from top-m bins
print("in-sample reconstruction from the m largest coefficients (an upper bound: it uses the answer) | r^2 with S | share of the lowest 1.5% of S found in the lowest 1.5% of the reconstruction | same for the lowest 10^-4 in the lowest 1.5%")
thr = np.quantile(xs, 0.015); low = xs <= thr; thr4 = np.quantile(xs, 1e-4); low4 = xs <= thr4
for m in (1000, 10 ** 4, 10 ** 5, 10 ** 6):
    G = np.zeros_like(F); sel = order[:m] + 1; G[sel] = F[sel]; y = np.fft.irfft(G, L); c = np.corrcoef(xs, y)[0, 1]
    ty = np.quantile(y, 0.015); print(f"  m={m} | {c*c:.4f} | {(low & (y <= ty)).sum()/low.sum():.4f} | {(low4 & (y <= ty)).sum()/low4.sum():.4f}")
del F, Fp, xs, xp
# ---- E. autocorrelation at every lag (linear, zero padded)
L2 = 1 << 26; A = np.fft.rfft(x, L2); A = A.real ** 2 + A.imag ** 2; ac = np.fft.irfft(A, L2)[:K // 2 + 1]; del A
lags = np.arange(len(ac)); corr = ac / ((K - lags) * var); zs = corr * np.sqrt(K - lags)
print(f"autocorrelation at lags 1..{len(ac)-1}: sd of z {zs[1:].std():.4f}; expected maximum of |z| for noise {math.sqrt(2*math.log(2*len(ac))):.2f}")
smallfac = np.zeros(len(ac), dtype=np.int64)
for r in primes(467, 100000):
    r = int(r); sel = np.arange(r, len(ac), r); smallfac[sel[smallfac[sel] == 0]] = r
free = (smallfac == 0); free[0] = False
print(f"lags NOT divisible by any prime 467..10^5 ({int(free.sum())} lags): max |z| {np.abs(zs[free]).max():.2f}, mean z^2 {np.mean(zs[free]**2):.4f}, mean z {zs[free].mean():+.5f}")
o = np.argsort(-np.abs(zs[1:]))[:15] + 1
print("15 largest |z|: (lag, z, corr, least later prime dividing the lag):", [(int(t), round(float(zs[t]), 1), round(float(corr[t]), 5), int(smallfac[t])) for t in o])
for T in (1, 2, 6, 30, 210, 2310, 30030, 510510, 9699690, 467, 479, 487, 467 * 479, 467 * 487, 2 * 467, 997, 1999, 4999, 9973, 99991):
    if T < len(ac): print(f"  lag {T}: corr {corr[T]:+.6f}  z {zs[T]:+.2f}")
big = np.nonzero(np.abs(zs) > math.sqrt(2 * math.log(2 * len(ac))) + 0.5)[0]; big = big[big > 0]
print(f"lags with |z| above the noise maximum + 0.5: {len(big)}; of these divisible by a prime 467..10^5: {int((smallfac[big] > 0).sum())}; largest least-prime among them {int(smallfac[big].max()) if len(big) else 0}")
# ---- F. interval hierarchy: variance of block means
print("interval hierarchy: block length | Var(block mean) * length / Var S  (1 = no structure in the order of k)")
for j in (1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20):
    Lb = 1 << j; nbk = K // Lb; bm = x[:nbk * Lb].reshape(nbk, Lb).mean(axis=1); print(f"  2^{j} | {bm.var()*Lb/var:.4f}  ({nbk} blocks, se {math.sqrt(2/nbk):.4f})")

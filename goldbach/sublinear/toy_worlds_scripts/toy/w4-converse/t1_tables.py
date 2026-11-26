#!/usr/bin/env python3
"""t1: the tables themselves.
 (a) Proposition C: the rows above 463 are exactly the odd q in (463, Q) with q mod r not in {0, a_r} for the 89 cover primes
     (467^2 > Q): R is an interval intersected with a product set.
 (b) per later prime s: mean, variance/mean (Poisson = 1 - 1/s), maximum, zero classes, rates in rows per nat:
     pin = (max - mean)/ln s, free list = max over j of (mean of the j heaviest classes - mean)/ln(s/j),
     thin = excluding the empty classes: gain/cost.
 (c) variance of the first-order score by range of primes (all primes to 10^8; above Q the table is the indicator of R).
 (d) the window and the pins that fit it."""
import math, numpy as np
from common import *
cov, rows = load(); n = len(rows)
print(f"(a) cover primes {len(cov)}, largest {cov[-1][0]}; rows {n}; rows <= 463: {int((rows <= 463).sum())} ({[int(x) for x in rows[rows <= 463]]})")
q = np.arange(Q); ok = (q % 2 == 1)
for r, a in cov: ok &= (q % r != 0) & (q % r != a)
S = set(int(x) for x in q[ok & (q > 463)]); Rhi = set(int(x) for x in rows[rows > 463])
print(f"    sifted set {{463 < q < Q odd, q mod r not in {{0, a_r}} for all r}}: {len(S)} elements; equal to the rows above 463: {S == Rhi}; 467^2 = {467**2} > Q = {Q}")
dens = n / Q; print(f"    density of rows n/Q = {dens:.6f}; (1/2) prod (1 - 2/r) = {0.5 * math.prod(1 - 2 / r for r, _ in cov):.6f}")

print("(b) tables of the later primes")
LP = later_primes(464, 5000); print(f"    later primes in [467, 5000]: {len(LP)}")
def rates(t):
    s = len(t); m = t.mean(); srt = np.sort(t)[::-1].astype(float); cs = np.cumsum(srt); j = np.arange(1, s)
    gain = cs[:-1] / j - m; cost = np.log(s / j); fr = gain / cost; jb = int(np.argmax(fr))
    z = int((t == 0).sum()); thin = (m * z / (s - z)) / (-math.log(1 - z / s)) if z else 0.0
    return (srt[0] - m) / math.log(s), fr[jb], (jb + 1) / s, thin
rec = []
for s in LP:
    t = table(rows, s); m = t.mean(); v = t.var(); pin, fr, dens_fr, thin = rates(t)
    rec.append((s, m, v / m, t.max(), (t == 0).mean(), pin, fr, dens_fr, thin, v))
rec = np.array(rec)
for lo, hi in ((467, 600), (600, 1000), (1000, 2000), (2000, 3500), (3500, 5000)):
    k = (rec[:, 0] >= lo) & (rec[:, 0] < hi); r = rec[k]
    print(f"    s in [{lo},{hi}): primes {k.sum():3d}  mean table {r[:,1].mean():.3f}  var/mean {r[:,2].mean():.3f} +- {r[:,2].std()/math.sqrt(k.sum()):.3f}"
          f"  max {r[:,3].mean():.2f}  empty classes {r[:,4].mean():.3f}  rows/nat: pin {r[:,5].mean():.3f}  free list {r[:,6].mean():.3f} (density {r[:,7].mean():.3f})  thin {r[:,8].mean():.3f}")
print(f"    all {len(LP)} primes: var/mean {rec[:,2].mean():.4f} +- {rec[:,2].std()/math.sqrt(len(LP)):.4f}; pin {rec[:,5].mean():.3f}, free list {rec[:,6].mean():.3f}, thin {rec[:,8].mean():.3f} rows per nat")
print(f"    pin at 467: max {int(rec[0,3])}, mean {rec[0,1]:.3f}, (max-mean)/ln s = {rec[0,5]:.3f}; max/ln s = {rec[0,3]/math.log(467):.3f} rows per nat")

print("(c) variance of the first-order score S = sum_s f_s(N mod s), by range of primes")
AP = primes_upto(Q); AP = [int(x) for x in AP[AP > 463]]
var = {};
for s in AP:
    t = table(rows, s); var[s] = t.var()
# above Q: f_s = indicator of R: variance (n/s)(1 - n/s); sum over primes Q < s <= 10^8 by the prime number theorem with li
def li_sum(a, b, k=200000):
    # sum over primes a < s <= b of n/s (1 - n/s)  ~  integral of n/t (1-n/t) dt / ln t
    x = np.exp(np.linspace(math.log(a), math.log(b), k)); f = (n / x) * (1 - n / x) / np.log(x)
    return float(np.sum((f[1:] + f[:-1]) / 2 * np.diff(x)))
tail = li_sum(Q, 1e8); tot = sum(var.values()) + tail
print(f"    sum of variances: primes 467..Q exact {sum(var.values()):.1f}; Q..10^8 (integral) {tail:.1f}; total {tot:.1f} (sd {math.sqrt(tot):.1f} strikes)")
for hi in (509, 1000, 2000, 5000, 20000, 200000):
    part = sum(v for s, v in var.items() if s <= hi); print(f"    primes to {hi:6d}: {100 * part / tot:5.1f}% of the variance")
D = 0.0;
N0, M, K = window(cov); print(f"(d) window: M = 2 prod r has {len(str(M))} digits, ln M = {math.log(M):.2f}; members below 10^200: K = {K} = 2^{math.log2(K):.2f}, ln K = {math.log(K):.2f}")
best = (0, 0, 0)
ex = {int(r[0]): r[3] - r[1] for r in rec}; mx = {int(r[0]): r[3] for r in rec}
allp = primes_upto(60000); allp = [int(x) for x in allp[allp > 463]]
exa = {};
for s in allp:
    t = table(rows, s); exa[s] = (t.max() - t.mean(), t.max())
bp = max(((exa[s][0] + exa[s2][0], s, s2) for i, s in enumerate(allp) for s2 in allp[i + 1:] if s * s2 <= K and s < 4700), default=None)
print(f"    pairs of later primes with product <= K: best excess over the mean {bp[0]:.2f} rows at {bp[1]} x {bp[2]} (maxima {exa[bp[1]][1]}, {exa[bp[2]][1]}); 467*479*487 = {467*479*487} {'>' if 467*479*487 > K else '<='} K")
np.save("rec.npy", rec)

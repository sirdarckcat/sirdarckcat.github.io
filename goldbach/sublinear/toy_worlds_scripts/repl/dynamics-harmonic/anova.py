#!/usr/bin/env python3
"""(a)+(b), part 1: the exact hierarchy of the score on the real window.  First-order (single-prime) components of the exact
sieve count S_z(k), measured from class means over the whole window, against the tables; cumulative share by level."""
import sys, math, numpy as np
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows); z = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10 ** 5
S = np.fromfile(f"S_{z}.u16", dtype=np.uint16).astype(np.float64); assert len(S) == K
mu = S.mean(); var = S.var(); W = mu / n
print(f"depth {z}: K={K} mean {mu:.4f} var {var:.3f} sd {math.sqrt(var):.4f} W={W:.5f}  binomial nW(1-W)={n*W*(1-W):.2f}  ratio {var/(n*W*(1-W)):.4f}")
def primes(a, b):
    sv = np.ones(b + 1, bool); sv[:2] = False
    for i in range(2, int(b ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    p = np.nonzero(sv)[0]; return p[p >= a]
kk = np.arange(K, dtype=np.int64)
print("r | measured v_r (regression of the class means on the table) | table prediction W^2 Var f_r/(1-1/r)^2 | share of Var S | best class: rows hit, mean shift of S (measured)")
tot_meas = 0; tot_pred = 0; out = {}
P = primes(467, 3000)
for r in P:
    r = int(r); cls = kk % r; cnt = np.bincount(cls, minlength=r); sm = np.bincount(cls, weights=S, minlength=r); m = sm / cnt
    v = float(((m - mu) ** 2 * cnt).sum() / K) - var * (r - 1) / K
    # table: class of N for class c of k
    f = np.bincount(rows % r, minlength=r).astype(float)
    pred = W ** 2 * f.var() / (1 - 1 / r) ** 2 if r <= z else 0.0
    cN = (N0 % r + np.arange(r) * (M % r)) % r; g = f[cN] - n / r; beta = -float((cnt * (m - mu) * g).sum() / (cnt * g * g).sum()); v = beta ** 2 * f.var()      # regression on the table: unbiased by noise
    tot_meas += v; tot_pred += pred; out[r] = (v, pred, m.min() - mu, f.max())
    if r < 520 or r in (997, 1999, 2999): print(f"{r} | {v:.4f} | {pred:.4f} | {v/var:.5f} | {int(f.max())} rows, {m.min()-mu:+.3f}")
    if r in (509, 997, 1999, 2999): print(f"   cumulative to {r}: measured {tot_meas:.3f} ({tot_meas/var:.4f} of Var S), tables {tot_pred:.3f} ({tot_pred/var:.4f})")
# whole first-order part from the tables alone, by ranges
allp = primes(467, min(z, 10 ** 7)); cum = 0; marks = [509, 1000, 2000, 5000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8]; mi = 0; nfreq = 0
print("first-order share of Var S carried by the primes up to R (tables; exact for r>Q where f_r is an indicator) and number of frequencies t/r involved")
for r in allp:
    r = int(r)
    while mi < len(marks) and r > marks[mi]: print(f"  R={marks[mi]}: {cum/var:.4f}   frequencies {nfreq}"); mi += 1
    if r < 200000:
        f = np.bincount(rows % r, minlength=r); vf = float((f.astype(float) ** 2).sum() / r - (n / r) ** 2)
    else: vf = n / r - (n / r) ** 2
    cum += W ** 2 * vf / (1 - 1 / r) ** 2; nfreq += r - 1
tail = 0.0
if z > 10 ** 7:   # r in (1e7, z]: sum of n/r by Mertens
    tail = W ** 2 * n * (math.log(math.log(z)) - math.log(math.log(1e7)))
while mi < len(marks) and marks[mi] <= z:
    extra = tail if marks[mi] > 10 ** 7 else 0
    print(f"  R={marks[mi]}: {(cum+extra)/var:.4f}   frequencies {nfreq if marks[mi] <= 10**7 else '2.7e14'}"); mi += 1
print(f"  model W ln(1/W)/(1-W) = {W*math.log(1/W)/(1-W):.4f}")

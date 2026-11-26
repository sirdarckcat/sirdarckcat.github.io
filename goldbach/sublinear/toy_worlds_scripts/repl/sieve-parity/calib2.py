#!/usr/bin/env python3
"""Feature screen with proper p-values: numeric and two-class features by a correlation z, many-class features by chi-square converted to the
   normal-equivalent |z| of its p-value; permutation null with 400 shuffles of the labels (one matrix product)."""
import math, numpy as np
from scipy import stats
d = np.load("features.npz"); y = d["y"].astype(np.float64); F = d["F"]; Cc = d["Cc"]; fn = list(d["fnames"]); cn = list(d["cnames"]); n = len(y)
leak = lambda name: ("(probable) prime" in name) or ("primes among" in name) or ("is prime" in name)
cols = []; names = []
for j, name in enumerate(fn):
    x = F[:, j].astype(np.float64)
    if x.std() > 0: cols.append((x - x.mean()) / x.std()); names.append(name)
multi = []
for j, name in enumerate(cn):
    x = Cc[:, j]; vals, inv = np.unique(x, return_inverse=True); cnt = np.bincount(inv)
    if (cnt >= 200).sum() < 2: continue
    if len(vals) == 2:
        b = (inv == 1).astype(np.float64); cols.append((b - b.mean()) / b.std()); names.append(name)
    else: multi.append((name, inv, cnt))
X = np.column_stack(cols).astype(np.float32); del cols
def screen(Y):                      # Y: n x m matrix of label vectors
    pb = Y.mean(0); Yc = (Y - pb).astype(np.float32)
    Z = (X.T @ Yc).astype(np.float64) / math.sqrt(n) / np.sqrt(pb * (1 - pb))            # features x m
    Zm = []
    for name, inv, cnt in multi:
        row = []
        for t in range(Y.shape[1]):
            pr = np.bincount(inv, weights=Y[:, t]); keep = cnt >= 200; p_ = pb[t]
            chi = (((pr - cnt * p_) ** 2) / (cnt * p_ * (1 - p_)))[keep].sum(); df = int(keep.sum()) - 1
            row.append(stats.norm.isf(stats.chi2.sf(chi, df) / 2))
        Zm.append(row)
    return np.vstack([Z, np.array(Zm)])
allnames = names + [m[0] for m in multi]; pat = np.array([not leak(nm) for nm in allnames])
Zr = screen(y[:, None])[:, 0]
print(f"{n} surviving rows of 4,300 real members, prime rate {y.mean():.5f}; {int(pat.sum())} features of the sieve pattern, of N and of q; {int((~pat).sum())} features that use the primality of other rows")
order = np.argsort(-np.abs(Zr))
print(f"pattern features: max |z| = {np.abs(Zr[pat]).max():.2f}, mean z^2 = {(Zr[pat] ** 2).mean():.3f}")
for i in order[:12]: print(f"   {Zr[i]:+.2f}  {allnames[i]}" + ("   [uses labels of other rows]" if not pat[i] else ""))
print("features using the primality of other rows: " + "; ".join(f"{allnames[i]}: {Zr[i]:+.2f}" for i in np.nonzero(~pat)[0]))
rng = np.random.default_rng(2026); mx = []; ms = []
for b in range(8):
    Y = np.column_stack([rng.permutation(y) for _ in range(50)]); Zp = screen(Y)[pat]
    mx += list(np.abs(Zp).max(0)); ms += list((Zp ** 2).mean(0))
mx = np.array(mx); ms = np.array(ms)
print(f"permutation null, {len(mx)} shuffles: max |z| median {np.median(mx):.2f}, 5% to 95%: {np.quantile(mx, .05):.2f} to {np.quantile(mx, .95):.2f}; share with max |z| >= the real one: {(mx >= np.abs(Zr[pat]).max()).mean():.3f}")
print(f"                                mean z^2: mean {ms.mean():.3f}, sd {ms.std():.3f}, 5% to 95%: {np.quantile(ms, .05):.3f} to {np.quantile(ms, .95):.3f}; share with mean z^2 >= the real one: {(ms >= (Zr[pat] ** 2).mean()).mean():.3f}")

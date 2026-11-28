#!/usr/bin/env python3
"""t2: additive structure of the real tables.
 (a) additive Fourier transform of each table: mean and largest power against a shuffled table (classes permuted at random).
 (b) the structure that Proposition C forces: R = interval x product set, so the classes c of s with c = b (mod D), D | 2*3*5*7*...,
     hold a number of candidates (integers of the allowed classes modulo D) that depends on b only through the last incomplete
     period.  For D in {6, 30, 210, 2310}: correlation of the table with its candidate count; the best list {c < s : c = b (mod D)}
     (one arithmetic progression of classes: lattice-compatible), its gain in rows over a random member and its rate in rows per
     nat of constraint ln(s/|list|); the same predicted from the candidate counts alone, and on shuffled tables.
 (c) additive energy of the heavy list of each table against random sets of the same size (all additive structure at once)."""
import math, sys, numpy as np
from common import *
cov, rows = load(); n = len(rows); rng = np.random.default_rng(7)
cl = dict(cov)
def indicator(D):
    q = np.arange(Q); ok = np.ones(Q, dtype=bool)
    if D % 2 == 0: ok &= (q % 2 == 1)
    for r in (3, 5, 7, 11, 13):
        if D % r == 0: ok &= (q % r != 0) & (q % r != cl[r])
    return ok
DS = (6, 30, 210, 2310); IND = {D: indicator(D) for D in DS}
qq = np.arange(Q)

def modD(t, D):
    """best single class b mod D among the classes c < s: (gain, rate)"""
    s = len(t); c = np.arange(s); sums = np.bincount(c % D, weights=t, minlength=D); cnt = np.bincount(c % D, minlength=D)
    k = cnt > 0; mean_b = np.full(D, -1e9); mean_b[k] = sums[k] / cnt[k]
    b = int(np.argmax(mean_b)); gain = mean_b[b] - t.mean(); return gain, gain / math.log(s / cnt[b])

def energy(A, s):
    F = np.abs(np.fft.fft(A.astype(float))) ** 2; return float((F[1:] ** 2).sum()) / s

def run(primes, label, shuf=3, do_energy=True):
    out = []
    for s in primes:
        t = table(rows, s).astype(float); m = t.mean(); v = t.var()
        P = np.abs(np.fft.fft(t)) ** 2 / (s * v) if v > 0 else np.zeros(s)      # normalised so that the mean over h != 0 is 1 exactly
        mxr = P[1:].max() / math.log(s - 1)
        mxs = []; rs = {D: [] for D in DS}; es = []
        thr = np.sort(t)[::-1][max(1, s // 4) - 1]; A = t >= max(thr, 1); eA = energy(A, s) if do_energy else 0.0
        for _ in range(shuf):
            u = rng.permutation(t); Pu = np.abs(np.fft.fft(u)) ** 2 / (s * v); mxs.append(Pu[1:].max() / math.log(s - 1))
            for D in DS:
                if D < s: rs[D].append(modD(u, D))
        if do_energy:
            for _ in range(8): es.append(energy(rng.permutation(A), s))
        row = [s, mxr, np.mean(mxs), (eA - np.mean(es)) / (np.std(es) + 1e-12) if do_energy else 0.0, A.mean()]
        for D in DS:
            if D >= s: row += [0] * 7; continue
            cand = np.bincount(qq % s, weights=IND[D], minlength=s); pD = n / IND[D].sum()
            rho = np.corrcoef(t, cand)[0, 1] if cand.var() > 0 else 0.0
            g, r = modD(t, D); gp, rp = modD(pD * cand, D)
            row += [rho, g, r, gp, rp, np.mean([x[0] for x in rs[D]]), np.mean([x[1] for x in rs[D]])]
        out.append(row)
    out = np.array(out)
    print(f"{label}: {len(primes)} primes")
    print(f"   (a) largest additive power / ln s: real {out[:,1].mean():.3f} (max {out[:,1].max():.2f} at s = {int(out[np.argmax(out[:,1]),0])}), shuffled {out[:,2].mean():.3f}")
    if do_energy: print(f"   (c) additive energy of the heavy list (density {out[:,4].mean():.2f}): z against random sets of that size: mean {out[:,3].mean():+.2f}, sd {out[:,3].std():.2f}, sd of the mean {out[:,3].std()/math.sqrt(len(out)):.2f}")
    for i, D in enumerate(DS):
        o = out[:, 5 + 7 * i: 12 + 7 * i]; k = out[:, 0] > D
        if k.sum() == 0: continue
        o = o[k]
        print(f"   (b) D = {D:5d}: corr(table, candidates) {o[:,0].mean():+.4f} (R^2 {np.mean(o[:,0]**2):.4f});  best class mod D: gain real {o[:,1].mean():.4f} rows, predicted {o[:,3].mean():.4f}, shuffled {o[:,5].mean():.4f};"
              f"  rate real {o[:,2].mean():.4f}, predicted {o[:,4].mean():.4f}, shuffled {o[:,6].mean():.4f} rows/nat")
    return out

LP = later_primes(464, 5000)
o1 = run(LP, "s in [467, 5000]")
big = primes_upto(600000)
for lo, hi, step in ((5000, 20000, 20), (20000, 60000, 60), (60000, 200000, 200), (200000, 600000, 400)):
    pr = [int(x) for x in big[(big >= lo) & (big < hi)]][::step]
    run(pr, f"s in [{lo}, {hi}), every {step}th prime", shuf=2, do_energy=False)
np.save("t2_small.npy", o1)

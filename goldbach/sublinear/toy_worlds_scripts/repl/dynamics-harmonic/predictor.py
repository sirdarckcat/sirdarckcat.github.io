#!/usr/bin/env python3
"""(b): are the members with extreme sieve count predicted by a few dominant frequencies?  Real window, truth = exact count
to 10^8.  Predictors: (i) L_R = sum over the later primes r <= R of the first-order table of r (a trigonometric polynomial
with the frequencies t/r, r <= R: the 'major arcs'); (ii) S_R = the exact count to depth R (every frequency whose
denominator is a product of primes <= R; the best mean-square predictor from those residues in the product model).
Also the anatomy of the extreme members and the nested best sub-windows inside the window."""
import sys, math, numpy as np
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows)
ld = lambda z: np.fromfile(f"S_{z}.u16", dtype=np.uint16)
S8 = ld(10 ** 8).astype(np.float64); mu = S8.mean(); var = S8.var(); W8 = mu / n
ps = 0.024 / 0.336642; lam = -math.log(1 - ps); w = np.exp(-lam * (S8 - mu)); wt = w.sum()
print(f"truth: depth 1e8 mean {mu:.3f} var {var:.3f}; weight of a member exp(-{lam:.4f} S)")
def report(name, Y, extra=""):
    c = np.corrcoef(Y, S8)[0, 1]; out = [f"{c*c:.4f}"]
    o = np.argsort(Y, kind="stable"); cw = np.cumsum(w[o]) / wt
    for phi in (0.015, 0.001, 0.0001):
        m = int(phi * K); out.append(f"{cw[m-1]:.4f} ({math.log(cw[m-1]/phi):+.2f})")
    t8 = np.sort(S8)[int(1e-4 * K)]; low = S8 <= t8; sel = np.zeros(K, bool); sel[o[:int(0.015 * K)]] = True
    out.append(f"{(low & sel).sum()/low.sum():.4f}")
    print(f"  {name} | " + " | ".join(out) + extra, flush=True)
print("predictor | r^2 with S | share of the total weight held by its lowest 1.5% (nats gained over random) | lowest 0.1% | lowest 0.01% | share of the true lowest 10^-4 members inside its lowest 1.5%")
report("S itself (depth 1e8)", S8)
def primes(a, b):
    sv = np.ones(b + 1, bool); sv[:2] = False
    for i in range(2, int(b ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    p = np.nonzero(sv)[0]; return p[p >= a]
kk = np.arange(K, dtype=np.int64); Lr = np.zeros(K); nfreq = 0; marks = {509: 0, 997: 0, 1999: 0, 2999: 0}; comp = {}
low4 = S8 <= np.sort(S8)[int(1e-4 * K)]; z4 = (S8[low4].mean() - mu); print(f"  (lowest 1e-4: {int(low4.sum())} members, mean S - mean = {z4:.2f} = {z4/math.sqrt(var):.2f} sd)")
anat = []
for r in primes(467, 2999):
    r = int(r); cls = kk % r
    # class of N for class c of k:  N = N0 + k M
    f = np.bincount(rows % r, minlength=r).astype(float); cN = (N0 % r + np.arange(r) * (M % r)) % r
    tab = -(W8 / (1 - 1 / r)) * (f[cN] - n / r)            # first-order table of r from the rows alone (no scan)
    comp_r = tab[cls]; Lr += comp_r; nfreq += r - 1
    anat.append((r, tab.var(), comp_r[low4].mean(), float((cls[low4] == np.argmin(tab)).mean()) if (tab == tab.min()).sum() == 1 else float("nan")))
    if r in marks: report(f"L_R, R={r} ({nfreq} frequencies, tables only)", Lr.copy())
for R in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    SR = ld(R).astype(np.float64); WR = SR.mean() / n
    report(f"S_R, R={R:.0e}", SR, f" | model r^2 = (W_z/W_R)^2 Var S_R / Var S_z = {(W8/WR)**2*SR.var()/var:.4f}")
print("anatomy of the lowest 10^-4 members: prime r | Var of its component | mean of its component over those members | Gaussian-conditioning prediction (S-mean)*Var_r/Var | share of those members in the best class of r (1/r = chance)")
for r, v, m, b in anat[:8] + anat[80:83]: print(f"  {r} | {v:.4f} | {m:+.4f} | {z4*v/var:+.4f} | {b:.5f} (chance {1/r:.5f})")
tv = sum(a[1] for a in anat); tm = sum(a[2] for a in anat); print(f"  all {len(anat)} primes to 2999: Var {tv:.2f} ({tv/var:.4f} of Var S); mean total component {tm:+.3f}; prediction {z4*tv/var:+.3f}; so {tm/z4:.4f} of the excursion of an extreme member comes from these {nfreq} frequencies")
bb = np.array([a[3] for a in anat if a[3] == a[3]]); rr = np.array([a[0] for a in anat if a[3] == a[3]]); print(f"  mean over primes of (share in best class)*r: {np.mean(bb*rr):.3f} (1 = chance)")
# nested best sub-windows inside the window (multi-scale search with exact tables)
print("nested best sub-windows inside the window: classes fixed | members | mean S - window mean | ln(mean weight / window mean weight) nats | room spent, nats")
sel = np.ones(K, bool); room = 0
for r in (467, 479, 487):
    cls = kk % r; f = np.bincount(rows % r, minlength=r).astype(float); cN = (N0 % r + np.arange(r) * (M % r)) % r
    best = int(np.argmax(f[cN])); sel &= (cls == best); room += math.log(r)
    if sel.sum() == 0: print(f"  +{r}: empty"); break
    print(f"  +{r} (class of k {best}, {int(f.max())} rows struck) | {int(sel.sum())} | {S8[sel].mean()-mu:+.3f} | {math.log(w[sel].mean()/w.mean()):+.4f} | {room:.2f}")

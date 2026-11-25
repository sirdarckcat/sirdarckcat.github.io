"""Are the N below X a fair sample of the class vectors, in the tail?  (The assumption behind a count made by
reweighting class vectors, which is how the prize of an ideal order is computed at 200 digits.)

Exact: the joint histogram of (k1, k2) = rows left at the line and at full depth over every member below X (truth2.c).
Ensemble: the same histogram over class vectors drawn uniformly at random (ensemble.c), scaled to the same number.
Printed: the moments, the tail of k2 level by level (exact count, ensemble count, ratio, deviation in standard
errors), the cover nats of the tiers, and the prize three ways: with the true successes; with the exact histogram
and the chance (1 - p)^k2 for a member with k2 rows left; with the ensemble histogram and the same chance.
  python fair_sample.py NAME EXACT_PREFIX... -- ENSEMBLE_PREFIX..."""
import math, sys
import numpy as np
from miniature2 import load, examined
i = sys.argv.index("--"); name = sys.argv[1]
cnt, suc = load(sys.argv[2:i]); ens, _ = load(sys.argv[i + 1:]); n = cnt.sum(); m = ens.sum(); S = suc.sum(); sc = n / m; k = np.arange(330)
def moments(c):
    t = c.sum(); c1 = c.sum(axis=1); c2 = c.sum(axis=0); m1 = (c1 * k).sum() / t; m2 = (c2 * k).sum() / t
    v1 = (c1 * (k - m1) ** 2).sum() / t; v2 = (c2 * (k - m2) ** 2).sum() / t; cov = ((k[:, None] - m1) * (k[None, :] - m2) * c).sum() / t
    return m1, math.sqrt(v1), m2, math.sqrt(v2), cov / math.sqrt(v1 * v2)
a = moments(cnt); b = moments(ens)
print(f"# {name}: {int(n):,d} members below X, {int(S):,d} successes; ensemble: {int(m):,d} random class vectors")
print(f"# exact:    k1 {a[0]:.3f} +- {a[1]:.3f}, k2 {a[2]:.3f} +- {a[3]:.3f}, correlation {a[4]:.4f}")
print(f"# ensemble: k1 {b[0]:.3f} +- {b[1]:.3f}, k2 {b[2]:.3f} +- {b[3]:.3f}, correlation {b[4]:.4f}")
c2 = cnt.sum(axis=0); e2 = ens.sum(axis=0); lo = int(min(np.nonzero(c2)[0][0], np.nonzero(e2)[0][0]))
print("k2 at most | members, exact | ensemble, scaled | ratio | deviation, standard errors | rarity, nats")
for t in range(lo, lo + 16):
    x = c2[:t + 1].sum(); y = e2[:t + 1].sum() * sc; se = math.sqrt(max(y, 1e-9) * (1 + sc))
    print(f"{t} | {int(x):,d} | {y:,.1f} | {x / y if y else float('nan'):.3f} | {(x - y) / se:+.1f} | {math.log(n / max(x, 1)):.2f}")
print("tier (k2 at most) | cover nats: exact | ensemble | mean k1 of the tier: exact | ensemble")
pa = cnt.sum(axis=1) / n; pb = ens.sum(axis=1) / m
lox = int(np.nonzero(c2)[0][0])
for t in range(lox + 1, lox + 8):
    out = []
    for c, p0 in ((cnt, pa), (ens, pb)):
        h = c[:, :t + 1].sum(axis=1); T = h.sum(); pt = h / T; ok = pt > 0
        out += [float((pt[ok] * np.log(pt[ok] / p0[ok])).sum()), float((pt * k).sum())]
    print(f"{t} | {out[0]:.2f} | {out[2]:.2f} | {out[1]:.2f} | {out[3]:.2f}")
if S > 0:
    s2 = suc.sum(axis=0); lev = np.nonzero(c2)[0]
    def nll(p):
        q = (1 - p) ** lev; return -float((s2[lev] * np.log(q) + (c2[lev] - s2[lev]) * np.log1p(-q)).sum())
    ps = np.linspace(0.2, 0.7, 5001); p = float(ps[np.argmin([nll(x) for x in ps])]); wgt = (1 - p) ** k
    print(f"# chance that a row left at full depth is prime, fitted to the successes by level: p = {p:.4f}; expected successes with it: exact histogram {float((c2 * wgt).sum()):,.1f}, ensemble {float((e2 * wgt).sum() * sc):,.1f}, true {int(S):,d}")
    print("successes wanted | prize, true successes | exact histogram with (1 - p)^k2 | ensemble with (1 - p)^k2 | N examined by the ideal order: true | exact histogram | ensemble")
    mc = cnt * wgt[None, :]; me = ens * sc * wgt[None, :]
    for t in (1, 3, 10, 30, 100, 300, 1000, 3000):
        if t > S / 2: break
        r = []
        for c, s in ((cnt, suc), (cnt, mc), (ens * sc, me)):
            r.append((examined(c.sum(axis=1), s.sum(axis=1), t), examined(c.sum(axis=0), s.sum(axis=0), t)))
        print(f"{t} | {math.log(r[0][0] / r[0][1]):.2f} | {math.log(r[1][0] / r[1][1]):.2f} | {math.log(r[2][0] / r[2][1]):.2f} | {r[0][1]:,.0f} | {r[1][1]:,.0f} | {r[2][1]:,.0f}")

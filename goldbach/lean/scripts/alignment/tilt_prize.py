"""Does the prize extrapolate by the tilt?  The two-criterion form of the tilt law, tested on exact miniatures.

Model: over the members, (k1, k2) = rows left at the line and at full depth are jointly normal with correlation r, and
a member succeeds with probability (1 - p)^k2.  Put theta = -ln(1 - p), lambda = theta x sd(k2).  Then the successes
are the members tilted by exp(-theta k2), and to collect the share f of all successes
   the ideal order (by k2) examines the share  Phi(Phi^-1(f) - lambda)    of the members,
   cover first (by k1)    examines the share  Phi(Phi^-1(f) - r lambda)  of the members,
so  prize(f) = ln Phi(Phi^-1(f) - r lambda) - ln Phi(Phi^-1(f) - lambda),
and of the rarity of a tier at z standard deviations of k2, the share r^2 of z^2/2 is cover.
Everything on the right is read off the joint histogram: r, sd(k2), and p by maximum likelihood from the successes
by level.
  python tilt_prize.py NAME PREFIX..."""
import math, sys
from statistics import NormalDist
import numpy as np
from miniature2 import load, examined
nd = NormalDist()
name = sys.argv[1]; cnt, suc = load(sys.argv[2:]); n = cnt.sum(); S = suc.sum(); k = np.arange(330)
c1 = cnt.sum(axis=1); c2 = cnt.sum(axis=0); s1 = suc.sum(axis=1); s2 = suc.sum(axis=0)
m1 = (c1 * k).sum() / n; m2 = (c2 * k).sum() / n; v1 = (c1 * (k - m1) ** 2).sum() / n; v2 = (c2 * (k - m2) ** 2).sum() / n
cov = float(((k[:, None] - m1) * (k[None, :] - m2) * cnt).sum() / n); r = cov / math.sqrt(v1 * v2); rho = cov / v1
print(f"# {name}: members {int(n):,d}, successes {int(S):,d}")
print(f"# k1: mean {m1:.2f}, sd {math.sqrt(v1):.3f}; k2: mean {m2:.2f}, sd {math.sqrt(v2):.3f}; regression of k2 on k1: slope {rho:.3f}; correlation r = {r:.3f}, r^2 = {r * r:.3f}")
if S > 0:
    # p by maximum likelihood from successes by level of k2
    lev = np.nonzero(c2)[0]; 
    def nll(p):
        q = (1 - p) ** lev; return -float((s2[lev] * np.log(q) + (c2[lev] - s2[lev]) * np.log1p(-q)).sum())
    ps = np.linspace(0.2, 0.7, 5001); p = float(ps[np.argmin([nll(x) for x in ps])]); th = -math.log(1 - p); lam = th * math.sqrt(v2)
    print(f"# chance that a row left at full depth is prime, fitted: p = {p:.4f}; theta = {th:.3f}; lambda = theta sd(k2) = {lam:.3f}; r lambda = {r * lam:.3f}")
    print(f"# mean k1 of the successes: {(s1 * k).sum() / S:.2f} (model: {m1 - th * cov:.2f}); mean k2 of the successes: {(s2 * k).sum() / S:.2f} (model: {m2 - th * v2:.2f})")
    print("successes wanted | share f | N examined, cover first: exact | model | ideal: exact | model | prize: exact | model")
    for t in (1, 3, 10, 30, 100, 300, 1000, 3000, 10000):
        if t > S / 2: break
        f = t / S; z = nd.inv_cdf(f); a = examined(c1, s1, t); b = examined(c2, s2, t)
        am = n * nd.cdf(z - r * lam); bm = n * nd.cdf(z - lam)
        print(f"{t} | {f:.5f} | {a:,.0f} | {am:,.0f} | {b:,.0f} | {bm:,.0f} | {math.log(a / b):.2f} | {math.log(am / bm):.2f}")
print("tier (k2 at most) | members | rarity | cover nats: exact | model r^2 z^2/2 with z from the tier's mean k2 | luck nats: exact")
pa = c1 / n
for t in range(int(np.nonzero(c2)[0][0]) + 2, int(np.nonzero(c2)[0][0]) + 9):
    h = cnt[:, :t + 1].sum(axis=1); T = h.sum(); pt = h / T; ok = pt > 0
    cover = float((pt[ok] * np.log(pt[ok] / pa[ok])).sum()); rar = math.log(n / T)
    zt = (m2 - float((cnt[:, :t + 1].sum(axis=0) * k[:t + 1]).sum() / T)) / math.sqrt(v2)          # mean k2 of the tier in sd below the mean
    print(f"{t} | {int(T):,d} | {rar:.2f} | {cover:.2f} | {r * r * zt * zt / 2:.2f} | {rar - cover:.2f}")

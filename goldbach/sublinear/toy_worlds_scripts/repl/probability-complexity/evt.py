#!/usr/bin/env python3
"""evt.py: extreme-value statistics of the exact sieve count (depth 10^8) over the whole real window (21,378,978 members)."""
import numpy as np, math
from statistics import NormalDist
ND = NormalDist()
h = np.load("hist.100000000.npy").astype(np.float64); K = h.sum(); s = np.arange(len(h))
mu = (h * s).sum() / K; var = (h * (s - mu) ** 2).sum() / K; sd = math.sqrt(var)
sk = (h * (s - mu) ** 3).sum() / K / sd ** 3; ku = (h * (s - mu) ** 4).sum() / K / var ** 2 - 3
n = 1502; w = mu / n; p = 0.023983426260108572; lam = -math.log(1 - p); lamp = -math.log(1 - p / w)
print(f"K {K:.0f} mean {mu:.4f} sd {sd:.4f} skew {sk:+.4f} ex.kurt {ku:+.4f}; w {w:.6f}; var/binomial {var/(n*w*(1-w)):.4f}; binomial skew {(1-2*w)/math.sqrt(n*w*(1-w)):+.4f}")
print(f"lambda' {lamp:.6f}; tau = lambda' sd = {lamp*sd:.4f}")
hit = h * np.exp(-lamp * s); Ht = hit.sum()
print(f"ln mean hit chance over the window: {math.log(Ht/K):.4f}; -lambda n = {-lam*n:.4f}; Gaussian formula -lam' mu + tau^2/2 = {-lamp*mu+(lamp*sd)**2/2:.4f}")
print(f"hit mass sits at S: mean {(hit*s).sum()/Ht:.2f} (z = {((hit*s).sum()/Ht-mu)/sd:+.3f}; Gaussian tilt predicts z = -tau = {-lamp*sd:+.3f})")
# lower tail against models
cum = np.cumsum(h)
def edge(x):      # Edgeworth with skewness and kurtosis, continuity corrected
    z = (x + 0.5 - mu) / sd; phi = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    return ND.cdf(z) - phi * (sk / 6 * (z * z - 1) + ku / 24 * (z ** 3 - 3 * z) + sk * sk / 72 * (z ** 5 - 10 * z ** 3 + 15 * z))
print("lower tail: s | members with S <= s | K*Normal | K*Edgeworth(skew,kurt)")
for x in (412, 414, 416, 418, 420, 425, 430, 440, 450, 460, 467):
    print(f"  {x} | {cum[x]:.0f} | {K*ND.cdf((x+0.5-mu)/sd):.2f} | {K*edge(x):.2f}")
print("upper tail: s | members with S >= s | K*Normal | K*Edgeworth")
for x in (605, 600, 595, 590, 580, 570):
    print(f"  {x} | {K-cum[x-1]:.0f} | {K*(1-ND.cdf((x-0.5-mu)/sd)):.2f} | {K*(1-edge(x-1)):.2f}")
smin = int(np.nonzero(h)[0][0])
print(f"minimum over the window: {smin} (z = {(smin-mu)/sd:.3f}); Normal law of the minimum: median {mu+sd*ND.inv_cdf(math.log(2)/K):.1f}, P(min <= 412) = {1-math.exp(-K*ND.cdf((412.5-mu)/sd)):.3f}; Edgeworth: P(min <= 412) = {1-math.exp(-K*edge(412)):.3f}")
# selection: share of the hit mass in the lowest fraction
hc = np.cumsum(hit)
print("selection by a cut S <= t: keep fraction | t | share of hit mass | gain ln(share/keep) | Gaussian ln(Phi(z+tau)/Phi(z))")
tau = lamp * sd
base = None
for t in (467, 462, 450, 439, 430, 421, 412):
    kf = cum[t] / K; sh = hc[t] / Ht; g = math.log(sh / kf); z = (t + 0.5 - mu) / sd
    if t == 467: base = g
    print(f"  {kf:.3e} | {t} | {sh:.4f} | {g:.3f} (vs the 1.5% keep {g-base:+.3f}) | {math.log(ND.cdf(z+tau)/ND.cdf(z)):.3f}")
gbest = math.log(math.exp(-lamp * smin) / (Ht / K))
print(f"single best member (S = {smin}): hit chance / window mean = e^{gbest:.3f}; over the 1.5% keep {gbest-base:+.3f}; with the sieve free (+0.30): {gbest-base+0.30:+.3f}")
# cost per hit with the fleet's split (26% sieve, 74% tests at the 1.5% keep)
kf0 = cum[467] / K; cs = 0.26; ct = 0.74 / kf0
best = min(((cs + cum[t] / K * ct) / (hc[t] / Ht), t) for t in range(smin, 520))
c0 = (cs + kf0 * ct) / (hc[467] / Ht)
print(f"cost per hit: best cut S <= {best[1]} (keep {cum[best[1]]/K:.4f}): {math.log(c0/best[0]):+.3f} nats against the cut at 467")
# many windows: the best of W windows of K members (Edgeworth tail; root by bisection)
print("best member of W windows: W | z of the minimum | gain of that member over the window mean | sieve work spent, nats")
for W in (1, 10, 100, 1e4, 1e6, 1e9):
    lo, hi = 300.0, 500.0
    for _ in range(60):
        m = (lo + hi) / 2
        if W * K * edge(m) < 1: lo = m
        else: hi = m
    z = (lo - mu) / sd; print(f"  {W:.0e} | {z:.3f} (S about {lo:.0f}) | {-lamp*(lo-mu)-tau*tau/2:.2f} | {math.log(W*K):.1f}")

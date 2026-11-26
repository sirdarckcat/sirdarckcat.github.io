# MODEL (not a measurement): what a free parity lambda(N - q) would be worth in the integer search at 200 digits,
# by the same selection identity that reproduces the toy's exact enrichments (analyse2.py, column "model E_o").
# Inputs taken from the programme's README: 1,502 rows after the cover, p = 0.0243 per row; after the sieve to 1e8
# about a third survive (S ~ 500, sd 18), keep 1.5% of members, which captures 0.199 of the hit mass.
from math import log, sqrt, erf
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
def zq(phi):                       # quantile by bisection
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if Phi(mid) < phi: lo = mid
        else: hi = mid
    return lo
rows, p = 1502, 0.0243; S, sdS = 500.0, 18.0; ps = rows * p / S
lam1 = -log(1 - ps); d1 = lam1 * sdS
lam2 = -log(1 - 2 * ps); sdo = sqrt(sdS ** 2 / 4 + S / 4); d2 = lam2 * sdo
print(f"per survivor p = {ps:.4f}; tilt of the hits in S: {d1:.2f} sd; with parity (odd survivors o, sd {sdo:.1f}, 2p each): {d2:.2f} sd")
for phi in (0.015, 0.008, 0.001):
    z = zq(phi); c1 = Phi(z + d1); c2 = Phi(z + d2)
    t1 = (1 - (1 - ps) ** (S + z * sdS)) / ps; t2 = (1 - (1 - 2 * ps) ** (S / 2 + z * sdo)) / (2 * ps)
    print(f"  keep {phi}: capture by S {c1:.3f} (README: 0.199 at 1.5%), by o {c2:.3f}; tests per kept member {t1:.1f} -> {t2:.1f};"
          f" hits per test x{c2 / c1 * t1 / t2:.2f} = {log(c2 / c1 * t1 / t2):.2f} nats")
print("cover only (no member sieve): o ~ Bin(1502, 1/2), sd %.1f, tilt %.2f sd; enrichment at keep 1%%: %.1f" % (sqrt(rows) / 2, -log(1 - 2 * p) * sqrt(rows) / 2, Phi(zq(0.01) - log(1 - 2 * p) * sqrt(rows) / 2) / 0.01))

# Item 1 (research, 25 Nov): the score exact to 1e6 for every member and to 1e8 only for the emptiest f of them (by the 1e6
# count): the share of the hit mass captured at a final keep of 1.5%, against the full count. An independent bivariate normal
# calculation from the Lean session's profile (94e40c5, goldbach/lean/scripts/alignment/profile_analysis.txt): nine ranges of
# primes, the innovation e_j of range j (rows newly struck minus a_j times the rows left before it) uncorrelated across ranges.
# With L_j the rows left after range j: L_j = (1 - a_j) L_{j-1} - e_j, so
#   S6 - E S6 = -sum_{j<=7} e_j prod_{j<i<=7} (1 - a_i),   S8 - E S8 = (1-a8)(1-a9)(S6 - E S6) - (1-a9) e_8 - e_9.
# The hit mass of a member is (1 - p8)^S8 = exp(-lam8 S8): it tilts the bivariate normal by -lam8 * (Cov(S6,S8), Var S8).
#   python3 item1_two_stage.py
import math
import numpy as np
from scipy.stats import norm, multivariate_normal

a  = [0.1058, 0.1359, 0.1298, 0.1058, 0.1045, 0.0567, 0.1164, 0.1428, 0.1250]
sd = [10.87, 11.81, 11.07, 9.59, 9.12, 6.55, 8.84, 9.11, 7.95]
def var_after(J):          # variance of the rows left after range J (1-based), from the innovations
    v = 0.0
    for j in range(J):
        f = math.prod(1 - a[i] for i in range(j + 1, J)); v += (sd[j] * f) ** 2
    return v
V6, V8 = var_after(7), var_after(9)
f89 = (1 - a[7]) * (1 - a[8]); C68 = f89 * V6
p8 = 0.0716; lam8 = -math.log1p(-p8)
print(f"from the innovations: Var S6 = {V6:.1f}, Var S8 = {V8:.1f} (measured 325.27), corr(S6, S8) = {C68 / math.sqrt(V6 * V8):.4f} (uarch: 0.78)")
# rescale so that Var S8 is the measured 325.27 (the innovations' sds are rounded in the table)
k = 325.27 / V8; V6 *= k; V8 *= k; C68 *= k
s6, s8 = math.sqrt(V6), math.sqrt(V8); rho = C68 / (s6 * s8)
# tilted means in standard units: S8 shifted by -lam8*V8, S6 by -lam8*C68
m8 = -lam8 * V8 / s8; m6 = -lam8 * C68 / s6
print(f"after rescaling: sd S6 {s6:.2f}, sd S8 {s8:.2f}, rho {rho:.4f}; tilt: S8 {m8:.3f} sd, S6 {m6:.3f} sd")
keep = 0.015
z = norm.ppf(keep)
full = norm.cdf(z - m8)
print(f"full count (exact to 1e8 for all), keep 1.5%: captured {full:.4f}")
only6 = norm.cdf(z - m6)
print(f"exact to 1e6 only, keep 1.5%: captured {only6:.4f} ({only6 / full:.3f} of the full count)")
# exact to 1e7 only: ranges 1..8
V7 = var_after(8) * k; C78 = (1 - a[8]) * V7; m7 = -lam8 * C78 / math.sqrt(V7)
print(f"exact to 1e7 only, keep 1.5%: captured {norm.cdf(z - m7):.4f} ({norm.cdf(z - m7) / full:.3f}); corr(S7, S8) {C78 / math.sqrt(V7 * V8):.4f} (uarch 0.90)")
def two_stage(f1, keep):
    """keep the emptiest f1 by S6, then the emptiest by S8 among them so that 'keep' of all members are kept."""
    t1 = norm.ppf(f1)
    cov = [[1, rho], [rho, 1]]
    P = lambda t2, mu: multivariate_normal(mean=mu, cov=cov).cdf([t1, t2])
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if P(mid, [0, 0]) < keep: lo = mid
        else: hi = mid
    t2 = (lo + hi) / 2
    return P(t2, [m6, m8]), t2
for keep in (0.005, 0.0075, 0.015):
    zk = norm.ppf(keep); fullk = norm.cdf(zk - m8)
    out = [f"keep {100 * keep:.2f}%: full count {fullk:.4f}"]
    for f1 in (0.05, 0.10, 0.15, 0.20, 0.30):
        c, t2 = two_stage(f1, keep); out.append(f"top {int(100 * f1)}% {c:.4f} ({c / fullk:.3f})")
    print("; ".join(out))

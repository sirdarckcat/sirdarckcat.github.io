#!/usr/bin/env python3
"""I2 priced by the sieve: what the parity of Omega is worth as a function of u = ln x / ln z.
   (1) Dickman rho, Buchstab omega (stable integral forms); the law  mean lambda on z-rough = rho'(u)/omega(u).
   (2) F_q[x], exact: monic polynomials of degree n with no irreducible factor of degree <= d, by parity of the number of factors.
   (3) Z at 200 digits: a free parity oracle in the selection model of the search."""
import math, numpy as np
from fractions import Fraction
from math import comb
from statistics import NormalDist
h = 1e-3; U = 27; ng = int(round(U / h)) + 1; ug = np.arange(ng) * h; i1 = int(round(1 / h)); i2 = 2 * i1
rho = np.ones(ng)
for i in range(i1 + 1, ng):      # u rho(u) = int_{u-1}^{u} rho : positive terms only, relative precision kept
    rho[i] = h * (rho[i - i1] / 2 + rho[i - i1 + 1:i].sum()) / (ug[i] - h / 2)
om = np.zeros(ng); om[i1:i2 + 1] = 1 / ug[i1:i2 + 1]; W = ug * om
for i in range(i2 + 1, ng):      # (u omega)' = omega(u-1)
    W[i] = W[i - 1] + h * 0.5 * (om[i - 1 - i1] + om[i - i1]); om[i] = W[i] / ug[i]
R = lambda u: float(np.interp(u, ug, rho)); O = lambda u: float(np.interp(u, ug, om)); EG = math.exp(0.5772156649015329)
print(f"checks: rho(2) = {R(2):.6f} (1 - ln 2 = {1 - math.log(2):.6f}); rho(10) = {R(10):.4e} (literature 2.7702e-11); rho(20) = {R(20):.4e} (literature 2.4618e-29); e^gamma omega(8) = {EG * O(8):.9f}")
print("\n(1) u | excess of even over odd Omega among z-rough n, rho'(u)/omega(u) | P(prime | rough) = 1/(u omega(u)) | P(prime | rough, Omega odd) = 2/(u omega(u) + rho(u-1)) | ratio")
for u, what in ((2.5, ""), (3, ""), (3.6, "toy: degree 18, sieved to degree 5"), (4.5, "toy: degree 18, sieved to degree 4"), (6, "toy: degree 18, sieved to degree 3"), (9, ""), (16.67, "Z: 200 digits sieved to 1e12"), (20, "Z: 200 digits sieved to 1e10"), (25, "Z: 200 digits sieved to 1e8")):
    a = 1 / (u * O(u)); b = 2 / (u * O(u) + R(u - 1))
    print(f"   {u:5.2f} | {-R(u - 1) / (u * O(u)):+.3e} | {a:.5f} | {b:.5f} | {b / a:.4f}   {what}")
print("\n(2) exact in F_q[x]: n, d | monic of degree n with all irreducible factors of degree > d | odd number of factors | irreducible | P(irr | rough) | P(irr | rough, odd) | u = n/d")
def mobius(n):
    r = 1; p = 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0: return 0
            r = -r
        p += 1
    return -r if n > 1 else r
def irr(q, k): return sum(mobius(j) * q ** (k // j) for j in range(1, k + 1) if k % j == 0) // k
def rough_counts(q, n, d):
    a = [0] * (n + 1); b = [0] * (n + 1); a[0] = b[0] = 1
    for k in range(d + 1, n + 1):
        I = irr(q, k); na = [0] * (n + 1); nb = [0] * (n + 1)
        for j in range(0, n // k + 1):
            c = comb(I + j - 1, j)
            for t in range(0, n - j * k + 1):
                na[t + j * k] += a[t] * c; nb[t + j * k] += b[t] * c * (-1) ** j
        a, b = na, nb
    return a[n], b[n]
for q, n in ((3, 18), (5, 12), (9, 9), (3, 30)):
    for d in sorted(set(x for x in (1, 2, 3, 4, 5, 6, n // 3, n // 2) if x < n)):
        r, l = rough_counts(q, n, d); odd = (r - l) // 2; I = irr(q, n)
        print(f"   q={q}, n={n}, d={d} | {r} | {odd} | {I} | {I / r:.4f} | {I / odd:.4f} | {n / d:.2f}")
print("\n(3) Z, 200 digits, sieve to 1e8: a parity oracle for surviving rows, in the selection model of the search (exact binomial thinning)")
ND = NormalDist()
mS, sdS, p = 506.03, 18.34, 0.07146           # measured here on 4,300 members of the real cover (2,175,934 surviving rows, all tested)
Sg = np.arange(380, 640); pS = np.exp(-0.5 * ((Sg - mS) / sdS) ** 2); pS /= pS.sum()
T1 = 1 / p; T2 = 1 / (2 * p); cs = 1.0; ct = (74 / 26) / (0.015 * T1)     # the fleet's split: 26% sieve, 74% tests at a keep of 1.5%
hit = (1 - p) ** Sg
def baseline():
    b = None
    for c1 in Sg:
        m = Sg <= c1; v = (pS[m] * hit[m]).sum() / (cs + pS[m].sum() * T1 * ct)
        if b is None or v > b[0]: b = (v, c1, pS[m].sum())
    return b
b0 = baseline()
print(f"   baseline (cut on the count S, test survivors to the first prime): best keep {100 * b0[2]:.2f}% (S <= {b0[1]}); at the fleet's 1.5% keep the value is {math.log(((pS * hit)[Sg <= 466].sum() / (cs + pS[Sg <= 466].sum() * T1 * ct)) / b0[0]):+.3f} nats from it")
# exact: S_odd | S ~ Bin(S, 1/2); a member is a hit iff none of its odd-Omega survivors is prime, each prime with probability 2p
J = np.arange(0, 640)
lg = np.array([math.lgamma(x + 1) for x in range(0, 700)])
cumK = np.zeros((len(Sg), len(J))); cumM = np.zeros((len(Sg), len(J)))
for a, S_ in enumerate(Sg):
    j = np.arange(0, S_ + 1); pm = np.exp(lg[S_] - lg[j] - lg[S_ - j] - S_ * math.log(2)); mm = pm * (1 - 2 * p) ** j
    cumK[a, :S_ + 1] = np.cumsum(pm); cumK[a, S_ + 1:] = 1; cumM[a, :S_ + 1] = np.cumsum(mm); cumM[a, S_ + 1:] = mm.sum()
assert abs(cumM[100, -1] - (1 - p) ** Sg[100]) < 1e-12 * (1 - p) ** Sg[100] * 1e3
def staged(c, tests_only=False):
    """cut on S; buy the parity of every surviving row of the kept members at c Fermat tests a row; cut on the odd survivors; test those"""
    best = (0,)
    for a1 in range(0, len(Sg)):
        w = pS[:a1 + 1]; par_cost = (w * Sg[:a1 + 1]).sum() * c * ct
        if tests_only:
            v = (w * hit[:a1 + 1]).sum() / (cs + par_cost + w.sum() * T2 * ct); cand = (v, Sg[a1], None, w.sum(), w.sum())
            if v > best[0]: best = cand
            continue
        mass = w @ cumM[:a1 + 1]; keep2 = w @ cumK[:a1 + 1]; v = mass / (cs + par_cost + keep2 * T2 * ct); j = int(v.argmax())
        if v[j] > best[0]: best = (v[j], Sg[a1], j, w.sum(), keep2[j])
    return best
f = staged(0.0); g = staged(0.0, True)
print(f"   FREE parity: {math.log(f[0] / b0[0]):+.2f} nats (members kept on the count of odd survivors <= {f[2]}: {100 * f[4]:.3f}%; tests halved); {math.log(g[0] / b0[0]):+.2f} nats if it is used only to halve the tests")
print("   parity at a price of c Fermat tests per surviving row (bought for the members kept on S, then a second cut on the odd survivors):")
for c in (1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 2e-2, 3e-2, 0.1, 0.5):
    b = staged(c); print(f"      c = {c:g}: {math.log(b[0] / b0[0]):+.2f} nats (keep on S {100 * b[3]:.2f}%, kept after the parity cut {100 * b[4]:.3f}% of all)")
print("   parity bought row by row as the rows are reached (selection as now; each survivor reached costs c, and half of them a test):")
for c in (0.0, 1e-2, 0.1, 0.3, 0.5):
    b = max((pS[Sg <= c1] * hit[Sg <= c1]).sum() / (cs + pS[Sg <= c1].sum() * T1 * (c + 0.5) * ct) for c1 in Sg)
    print(f"      c = {c:g}: {math.log(b / b0[0]):+.2f} nats")

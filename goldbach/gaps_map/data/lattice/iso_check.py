# Second pair of eyes on the isolated-N loss (Research's README, "The prize, with the fleet's constants").
# Model: rows alive at depth z0 are struck by the primes in (z0, B] independently with probability 1 - ln z0/ln B (binomial survivors);
# an unselected member succeeds with probability E[(1-p_B)^S]; keeping the best fraction f by S keeps the share m(f) of the success mass.
import numpy as np, math
from math import lgamma, log, exp, sqrt
EG = 0.5772156649; lnN = 200 * log(10)
def pmf(n, q):
    k = np.arange(n + 1); lp = np.array([lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) for i in k]) + k * log(q) + (n - k) * log(1 - q); w = np.exp(lp - lp.max()); return w / w.sum()
def cost_per_unit_mass(n, z0, B, f, cs):
    """tests per unit of hit mass (one unit = the mean hit mass of one scanned member): (sieve + f * tests to a prime) / (share of the mass kept by the best fraction f)"""
    surv = log(z0) / log(B); pB = exp(EG) * log(B) / lnN; kappa = -log(1 - pB); v = 1 / pB
    w = pmf(n, surv); S = np.arange(n + 1); mass = w * np.exp(-kappa * S); mass /= mass.sum(); cum = np.cumsum(w)
    j = int(np.searchsorted(cum, f)); frac = cum[j]; share = mass[:j + 1].sum()
    return (cs + frac * v) / share, dict(v=v, share=share, frac=frac, sd=sqrt(n * surv * (1 - surv)), kappa=kappa)
print('(1) the fleet at 200,000: 1,502 rows alive at depth 463; sieve to B, keep the best fraction f, test them (tests to the first prime = 1/p_B)')
for B in (1e8, 1e9):
    for f in (0.015, 0.03):
        for cs in (0.0054, 0.0093, 0.0118):
            c, d = cost_per_unit_mass(1502, 463, B, f, cs); print('   B=%.0e f=%.3f sieve cost %.4f test: %.2f tests per unit of hit mass (kept %.1f%% of the mass; v = %.1f)' % (B, f, cs, c, 100 * d['share'], d['v']))
print('\n(2) an isolated ideal N: 1,116 rows alive at depth 2,000 (Result 3); cost of testing it as it comes, and with its own sieve to 10^6 then a cut at 3%')
for z0, rows in ((2000, 1116), (5000, 910), (20000, 685)):
    pz = 2 * math.prod(s / (s - 1) for s in [int(s) for s in range(3, z0 + 1) if all(s % d for d in range(2, int(s ** .5) + 1))]) / lnN
    print('   depth %5d: p_z = %.4f, tests to the first prime 1/p_z = %.1f -> against 1.5: %.2f nats' % (z0, pz, 1 / pz, log(1 / pz / 1.5)))
    for cs in (0.25, 0.65):
        c, d = cost_per_unit_mass(rows, z0, 1e6, 0.03, cs); print('      own sieve to 10^6 (%.2f test per N), keep 3%%: %.2f tests per unit of mass (kept %.1f%%) -> %.2f nats against 1.5' % (cs, c, 100 * d['share'], log(c / 1.5)))
print('\n(3) break-even budget for an enumerator of ideal N at depth 2,000: E + T = c_fleet * e^gain, gain = 5.9 nats (33.4 against 39.3)')
for cf in (1.43, 1.5): print('   c_fleet = %.2f: E + T = %.0f Fermat tests (T = 33 to reject, or 5 to 7 with own sieve and cut) ; 550 tests = 10^9 operations means %.1e operations per test' % (cf, cf * exp(5.9), 1e9 / 550))

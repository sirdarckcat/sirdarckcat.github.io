# Q1 stake of a cheaper sieve, with the Opus session's units: rho = (sieve cost per member)/(tests per kept member x test cost), a kept member costs v = 1/p' tests,
# so the sieve cost per member is c_s = rho * v tests. (My first sweep, q1_cost.py part (b), passed rho as c_s: wrong by the factor v = 14. Part (a) and (c) are in tests and stand.)
import numpy as np
from math import log, exp, lgamma, sqrt
EG = 0.5772156649; lnN = 200 * log(10)
def pmf(n, q):
    k = np.arange(n + 1); lp = np.array([lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) for i in k]) + k * log(q) + (n - k) * log(1 - q); w = np.exp(lp - lp.max()); return w / w.sum()
def cost(n, z0, B, f, cs, sdscale=0.9836):
    c = log(z0) / log(B); pB = exp(EG) * log(B) / lnN; kappa = -log(1 - pB); v = 1 / pB
    k = np.arange(n + 1); sd = sqrt(n * c * (1 - c)) * sdscale; mu = n * c
    w = np.exp(-0.5 * ((k - mu) / sd) ** 2); w /= w.sum(); mass = w * np.exp(-kappa * k); mass /= mass.sum(); cum = np.cumsum(w)     # normal law with the corrected sd
    j = int(np.searchsorted(cum, f)); frac = cum[j]; share = mass[:j + 1].sum()
    return (cs + frac * v) / share, v, share, frac
v = cost(1502, 463, 1e8, 0.015, 0)[1]; print('v = %.2f tests to a prime' % v)
base = None
print('rho    best keep   tests per unit of mass   gain over the 1.5%% keep at the same rho (nats)   [Opus table: 0.001: 0.47, 0.003: 0.17, 0.01: 0.003, 0.02: 0.03, 0.05: 0.21, 0.1: 0.42]')
for rho in (0.0003, 0.001, 0.003, 0.0054, 0.0118, 0.02, 0.05, 0.1):
    cs = rho * v
    fs = np.geomspace(1e-5, 0.6, 600); res = [cost(1502, 463, 1e8, f, cs) for f in fs]; i = int(np.argmin([r[0] for r in res]))
    c15 = cost(1502, 463, 1e8, 0.015, cs)[0]
    print('%.4f  %.2f%%     %.3f                    %.2f' % (rho, 100 * res[i][3], res[i][0], log(c15 / res[i][0])))
print()
print('stake of a cheaper sieve, all against the G4 as it is (rho = 0.0054, best keep 0.85%):')
c0 = min(cost(1502, 463, 1e8, f, 0.0054 * v)[0] for f in np.geomspace(1e-4, 0.3, 400))
for rho in (0.0054, 0.0027, 0.001, 0.0003, 0.0):
    c = min(cost(1502, 463, 1e8, f, rho * v)[0] for f in np.geomspace(1e-5, 0.3, 600)); print('   rho %.4f: %.3f tests per unit of mass, gain %.2f nats' % (rho, c, log(c0 / c)))

import numpy as np, math
from math import lgamma, log, exp
EG = 0.5772156649; lnN = 200 * math.log(10); n = 1502; r0 = 6.1379   # ln 463
def binom_pmf(n, q):
    k = np.arange(n + 1); lp = np.array([lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) for i in k]) + k * log(q) + (n - k) * log(1 - q); return np.exp(lp - lp.max()) / np.exp(lp - lp.max()).sum()
def analysis(B, cs, n=1502, verbose=True):
    lnB = math.log(B); surv = r0 / lnB; pB = EG and math.exp(EG) * lnB / lnN; kappa = -math.log(1 - pB); v = 1 / pB
    pmf = binom_pmf(n, surv); S = np.arange(n + 1); w = pmf * np.exp(-kappa * S)       # success mass by survivor count
    mean_succ = w.sum()                                                                   # P(success) of an unselected member
    base_cost = (cs + v) / mean_succ                                                      # sieve and verify every member
    best = (base_cost, 1.0)
    cum_p = np.cumsum(pmf); cum_w = np.cumsum(w)
    for f in np.logspace(-9, 0, 400):
        j = min(np.searchsorted(cum_p, f), n)                                                     # members with S <= j
        frac = cum_p[j]; m = cum_w[j]
        cost = (cs + frac * v) / m
        if cost < best[0]: best = (cost, frac)
    # maximum selection: verify only the single best member of the pool of J
    return dict(B=B, p=pB, surv=surv, kappa=kappa, v=v, sigma=math.sqrt(n * surv * (1 - surv)), base=base_cost, best=best[0], f=best[1], gain=math.log(base_cost / best[0]), mean_succ=mean_succ)
print('sieve depth B, p_B, tests to a prime v=1/p_B, survivors mean/sd, exponent of an unselected member, and the selection gain in cost per success (nats) at sieve cost cs (modexp-equivalents per member)')
for B in (2e3, 1e4, 1e6, 2e7, 1e9):
    for cs in (0.003, 0.01, 0.03, 0.1, 0.3):
        r = analysis(B, cs)
        print('B=%9.0f p_B=%.4f v=%5.1f sd=%5.1f  exponent(unselected)=%5.2f  cs=%.3f -> best f=%.2e, gain %.2f nats' % (B, r['p'], r['v'], r['sigma'], -math.log(r['mean_succ']), cs, r['f'], r['gain']))
    print()
# maximum gain for a pool of J members (verify only the best one): exponent reduction
for J in (2e7, 1e9, 1e12, 1e15):
    B = 2e7; lnB = math.log(B); surv = r0 / lnB; pB = math.exp(EG) * lnB / lnN; kappa = -math.log(1 - pB); pmf = binom_pmf(n, surv); cum = np.cumsum(pmf)
    s = np.searchsorted(cum, 1.0 / J); mean = n * surv
    print('pool %.0e: best survivors %d vs mean %.0f -> exponent reduction %.2f nats (infinite sieve budget)' % (J, s, mean, kappa * (mean - s)))

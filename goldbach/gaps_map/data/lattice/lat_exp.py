# Coppersmith with P = prod s^(e_s): optimise the exponents per prime (greedy on the marginal ratio) for the ratio agreement/sqrt(n lnK lnP).
import numpy as np, math, sys
from math import exp, log, lgamma
n = 1502; lnK = 16.9
def primes_upto(m):
    s = np.ones(m + 1, bool); s[:2] = False
    for i in range(2, int(m ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
ps = [int(p) for p in primes_upto(60000) if p > 463]; lam = np.array([n / s for s in ps]); lns = np.array([log(s) for s in ps])
def pois_tail(l, j):   # P(v > j) for Poisson(l)
    return 1.0 - sum(exp(-l + i * log(l) - lgamma(i + 1)) for i in range(j + 1))
# marginal value of raising e_s from j to j+1: lns * P(v > j), cost lns
e = np.zeros(len(ps), dtype=int); d = 0.0; lnP = 0.0; best = (0, None)
import heapq
heap = [(-pois_tail(l, 0), i) for i, l in enumerate(lam)]; heapq.heapify(heap)
while heap and lnP < 60000:
    negv, i = heapq.heappop(heap); v = -negv                      # largest marginal efficiency first
    d += lns[i] * v; lnP += lns[i]; e[i] += 1; r = d / math.sqrt(n * lnK * lnP)
    if r > best[0]: best = (r, (lnP, d, int(e.max()), int((e > 0).sum()), ps[int(np.max(np.nonzero(e)[0]))]))
    heapq.heappush(heap, (-pois_tail(lam[i], e[i]), i))
print('optimal per-prime exponents: best ratio %.3f at lnP = %.0f, agreement %.0f, max exponent %d, %d primes used, largest prime %d' % (best[0], *best[1]))
print('(uniform exponent, same model: 0.199 at z = 4000, e = 1; Research\'s grid maximum 0.200)')

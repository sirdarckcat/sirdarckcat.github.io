# Mean-field model of the greedy cover of greedy_cover.py (python3 greedy_meanfield.py x [x ...]): T targets spread over the r - 1 nonzero classes of the prime r like independent
# balls; the prime strikes the fullest class.  E[max] of r - 1 cells with Poisson(lam) each, lam = T / (r - 1).
import math, sys
import numpy as np
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
def emax(lam, cells):
    if lam <= 0: return 0.0
    if lam > 50:                                        # Gaussian regime with the usual extreme-value correction
        a = math.sqrt(2 * math.log(cells)); z = a - (math.log(math.log(cells)) + math.log(4 * math.pi)) / (2 * a) + 0.5772 / a
        return lam + z * math.sqrt(lam)
    m = np.arange(0, int(lam + 12 * math.sqrt(lam) + 40))
    logp = -lam + m * math.log(lam) - np.array([math.lgamma(v + 1) for v in m])
    cdf = np.minimum(1.0, np.cumsum(np.exp(logp)))
    return float(np.sum(1 - cdf ** cells))             # E[max] = sum_{m >= 0} P(max > m)
def left(x, y, PR):
    T = float(np.searchsorted(PR, y) - 1)              # odd primes below y
    for r in PR[1:]:
        if r > x: break
        if T <= 0: return 0.0
        k = emax(T / (r - 1), r - 1)
        T -= min(T, max(1.0, k))
    return T
def G(x, PR):
    lo, hi = x, int(3 * x * math.log(x) ** 2)
    while hi - lo > max(2, lo // 500):
        mid = (lo + hi) // 2
        if left(x, mid, PR) <= 0.5: lo = mid
        else: hi = mid
    return lo
PR = primes_upto(60_000_000)
for x in map(int, sys.argv[1:]):
    g = G(x, PR)
    print(f"x = {x}: mean-field greedy reaches {g}; / (x ln x) = {g / (x * math.log(x)):.2f}; / (x ln^2 x) = {g / (x * math.log(x) ** 2):.3f}", flush=True)

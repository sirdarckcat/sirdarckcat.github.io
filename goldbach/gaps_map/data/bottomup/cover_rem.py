# Rate of the cover as a Gaussian-tail selection: mean and sd of the number of alive rows over RANDOM class vectors, and what a random-energy model would give for the optimum.
import numpy as np, math, time
rng = np.random.default_rng(3)
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rows = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]
res = np.stack([rows % p for p in mods])                       # 89 x rows
lnM = sum(math.log(p) for p in mods)
def nalive(c): return int((~(res == c[:, None]).any(axis=0)).sum())
t0 = time.time(); S = 4000
vals = np.array([nalive(np.array([rng.integers(p) for p in mods])) for _ in range(S)]); print('random covers (all classes allowed incl. 0): %d samples in %.0f s: mean %.1f sd %.2f min %d max %d' % (S, time.time() - t0, vals.mean(), vals.std(), vals.min(), vals.max()))
vals2 = np.array([nalive(np.array([rng.integers(1, p) for p in mods])) for _ in range(S)]); print('random covers (nonzero classes): mean %.1f sd %.2f' % (vals2.mean(), vals2.std()))
from scipy.stats import skew, kurtosis
print('skewness %.3f excess kurtosis %.3f' % (skew(vals2), kurtosis(vals2)))
mu, sd = vals2.mean(), vals2.std(); lnM1 = sum(math.log(p - 1) for p in mods)
for lab, ln in (('all classes', lnM), ('nonzero classes', lnM1)):
    z = math.sqrt(2 * ln); print('REM (Gaussian) ground state with ln #covers = %.1f (%s): z = %.1f, n_min = %.0f - %.1f*%.2f = %.0f' % (ln, lab, z, mu, z, sd, mu - z * sd))
print('best found: annealing 1,524 (mine), campaign 1,502. rate of the cover: p*sd = %.3f nats per sd (p = 0.02398)' % (0.02398 * sd))

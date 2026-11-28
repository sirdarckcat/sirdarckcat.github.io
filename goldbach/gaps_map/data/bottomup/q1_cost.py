# Q1 (Research, 17:51 UTC): is anything better than sieving known for strike counts of polynomial values, and what is a faster sieve worth?
# (a) cost of the alternatives in Fermat tests on this machine (GMP calibration in gmp_cal.py: Fermat 77.6 us, mul 1.44e8 bits ~0.75 s)
# (b) the stake: fleet cost per unit of hit mass as a function of the sieve cost per member, optimum over the keep fraction f.
import sys, math
sys.path.insert(0, '../lattice')
import numpy as np
from math import log, exp, lgamma, sqrt
EG = 0.5772156649; lnN = 200 * log(10)
def pmf(n, q):
    k = np.arange(n + 1); lp = np.array([lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) for i in k]) + k * log(q) + (n - k) * log(1 - q); w = np.exp(lp - lp.max()); return w / w.sum()
def cost(n, z0, B, f, cs):
    surv = log(z0) / log(B); pB = exp(EG) * log(B) / lnN; kappa = -log(1 - pB); v = 1 / pB
    w = pmf(n, surv); S = np.arange(n + 1); mass = w * np.exp(-kappa * S); mass /= mass.sum(); cum = np.cumsum(w)
    j = int(np.searchsorted(cum, f)); frac = cum[j]; share = mass[:j + 1].sum()
    return (cs + frac * v) / share, v, share, frac
print('(a) tests (77.6 us each on this machine, GMP) to find the rows struck by primes up to B, per member (1,502 rows)')
tf = 77.6e-6; ghz = 3.5e9; cyc_test = tf * ghz
print('    one Fermat test = %.2e cycles' % cyc_test)
for B in (1e6, 1e7, 1e8):
    pi = B / (log(B) - 1.08); zbits = B * 1.4427 * 1.0       # theta(B)/ln 2 bits in the product of the primes
    # per-member root lookups: one reduction of N (11 limbs) per prime, 4 (SIMD) to 25 (scalar) cycles including the lookup
    lo, hi = pi * 4 / cyc_test, pi * 25 / cyc_test
    # Bernstein batch smooth part on 1,502 unrelated 665-bit numbers: batch K = zbits/665 numbers, remainder tree = c * log2(K) * M(L), c in 1..3, L = 2 zbits
    # M(L) from the GMP measurements: 1e6 bits 0.003 s, 1e7 0.044 s, 1e8 0.497 s, 3e8 1.914 s -> interpolate in log-log
    pts = [(1e6, 0.003), (1e7, 0.044), (1e8, 0.497), (3e8, 1.914)]
    def M(L):
        x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts]); return exp(np.interp(log(L), x, y, left=None))
    L = 2 * zbits; K = zbits / 665; lev = math.log2(K)
    b_lo, b_hi = 1 * lev * M(L) / K * 1502 / tf, 3 * lev * M(L) / K * 1502 / tf
    # direct: z mod F(N), F(N) = product of the rows (1e6 bits): (|z|/|F|) multiplications of 1e6 bits
    d = max(1, zbits / 1e6) * M(1e6) * 1.0 / tf
    print('    B=%.0e: per-N root lookups %.1f to %.1f tests; Bernstein batch on the rows %.0f to %.0f tests; z mod F(N) once per member %.0f tests; window sieve 0.005-0.012 tests' % (B, lo, hi, b_lo, b_hi, d))
print('\n(b) the stake of a cheaper sieve: tests per unit of hit mass at the best keep fraction (n = 1,502 alive at 463, B = 1e8 and 1e9)')
for B in (1e8, 1e9):
    base = None
    for cs in (0.0118, 0.0054, 0.0027, 0.001, 0.0003, 0.0):
        best = min(((cost(1502, 463, B, f, cs), f) for f in np.geomspace(1e-5, 0.5, 200)), key=lambda t: t[0][0])
        c, v, share, frac = best[0]
        if base is None: base = c
        print('    B=%.0e sieve %.4f test per member: best f = %.4f -> %.3f tests per unit of mass (gain %.2f nats over the first line; share kept %.1f%%)' % (B, cs, frac, c, log(base / c), 100 * share))
print('\n(c) the lone ideal N (1,116 rows alive at depth 2,000, own sieve to 1e6, keep 3%) against the sieve cost per N in Fermat tests')
for cs in (0.25, 0.65, 1.2, 2.5, 5, 7.3):
    c, v, share, frac = cost(1116, 2000, 1e6, 0.03, cs); print('    sieve %.2f test per N: %.2f tests per unit of mass -> %.2f nats against 1.5' % (cs, c, log(c / 1.5)))

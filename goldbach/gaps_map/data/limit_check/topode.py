import numpy as np, math, sys
from math import lgamma, log, exp, floor

def li(x):
    # logarithmic integral via series (Ramanujan) for x>2
    from math import log
    gamma = 0.5772156649015329
    lx = log(x); s = 0.0; term = 1.0; fact = 1.0
    # series: li(x) = gamma + ln ln x + sum_{k>=1} (ln x)^k/(k k!)
    s = gamma + log(lx); p = 1.0
    for k in range(1, 400):
        p *= lx / k
        s += p / k
        if p/k < 1e-12*abs(s): break
    return s
def pi_est(x): return li(x) - li(2) if x > 3 else 0

def emax_poisson(m, n):
    """E[max of n iid Poisson(m)] (n large) via sum_{k>=1} P(max>=k)."""
    if m <= 0: return 0.0
    # cdf recursively
    k0 = max(0, int(m - 8*math.sqrt(m) - 5))
    # P(X<=k0-1) negligible -> treat F(k)^n tiny
    tot = float(k0)
    # compute pmf at k0
    lp = -m + k0*log(m) - lgamma(k0+1)
    p = exp(lp)
    # cdf up to k0-1: compute by summation from 0 only if k0 small; else approximate as 0
    cdf = 0.0
    if k0 > 0:
        # accumulate from a lower start to get cdf(k0-1) approx
        j0 = max(0, k0 - int(12*math.sqrt(m)+20))
        pj = exp(-m + j0*log(m) - lgamma(j0+1)); c = 0.0
        for j in range(j0, k0):
            c += pj; pj *= m/(j+1)
        cdf = c
    k = k0
    pk = p
    while True:
        # P(max >= k+1) = 1 - F(k)^n where F(k)=cdf+pk
        F = cdf + pk
        Fk = F
        pm = 1.0 - exp(n * log(Fk)) if Fk < 1 else 0.0
        tot += pm
        cdf = F
        k += 1
        pk *= m / k
        if pm < 1e-9: break
    return tot

def top_greedy(U0, y1, x, nsub=0.004):
    """deterministic dynamic greedy over primes in (y1,x], binned. returns leftover U (<=0 means complete)."""
    U = float(U0)
    s = y1
    while s < x and U > 0:
        s2 = min(x, s * 1.02)
        cnt = pi_est(s2) - pi_est(s) if s2 > 50 else max(0.0, s2 - s) / log(max(s, 3))
        smid = math.sqrt(s*s2)
        remaining = cnt
        while remaining > 1e-9 and U > 0:
            m = U / (smid - 1)
            k = max(1.0, emax_poisson(m, smid - 1))
            step = min(remaining, max(1.0, nsub * U / k))
            U -= k * step
            remaining -= step
        s = s2
    return U

def critical_U0(y1, x):
    lo, hi = 1.0, 3.0 * x
    for _ in range(40):
        mid = 0.5*(lo+hi)
        if top_greedy(mid, y1, x) <= 0: lo = mid
        else: hi = mid
    return lo

if __name__ == '__main__':
    for x in [int(float(a)) for a in sys.argv[1:]]:
        lx = log(x); y1 = x/lx
        C = critical_U0(y1, x)
        print(f"x={x:g} y1={y1:.0f} C_top={C:,.0f}  C/x={C/x:.4f}  1/(lnln x)={1/log(lx):.4f}  C*lnln/x={C*log(lx)/x:.3f}", flush=True)

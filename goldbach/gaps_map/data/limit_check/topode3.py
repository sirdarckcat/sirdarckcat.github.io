import math, sys, time
import numpy as np
from scipy.special import gammaln
from math import log
from topode import pi_est

def emax_vec(m, n):
    """E[max of n iid Poisson(m)] via sum_k P(max>=k); vectorised."""
    if m <= 0: return 1.0
    kmax = int(m + 12*math.sqrt(m) + 80)
    k = np.arange(0, kmax + 1, dtype=float)
    # sf(k-1)=P(X>=k) computed by reverse cumsum of pmf
    lp = -m + k*np.log(m) - gammaln(k+1)
    pmf = np.exp(lp)
    sf_ge = np.cumsum(pmf[::-1])[::-1]            # P(X>=k)
    tail = -np.expm1(n*np.log1p(-np.minimum(sf_ge, 1-1e-16)))   # P(max>=k)
    tail[0] = 1.0
    return max(1.0, float(tail[1:].sum()))

def capacity_greedy(U0, y1, x, nsub=0.01, binw=1.03):
    U = float(U0); s = y1
    while s < x and U > 0:
        s2 = min(x, s*binw)
        cnt = pi_est(s2) - pi_est(s)
        smid = math.sqrt(s*s2)
        rem = cnt
        while rem > 1e-9 and U > 0:
            m = U/(smid-1)
            k = emax_vec(m, smid-1)
            step = min(rem, max(1.0, nsub*U/k))
            U -= k*step
            rem -= step
        s = s2
    return U

def crit(x, y1=None, iters=24):
    lx = log(x); y1 = y1 or x/lx
    lo, hi = 1.0, 3.0*x
    for _ in range(iters):
        mid = 0.5*(lo+hi)
        if capacity_greedy(mid, y1, x) <= 0: lo = mid
        else: hi = mid
    return lo

if __name__ == '__main__':
    for a in sys.argv[1:]:
        x = float(a); t = time.time(); lx = log(x); ll = log(lx)
        C = crit(x)
        print(f"x={x:.0e} ln x={lx:.1f} lnln={ll:.3f} C/x={C/x:.4f}  C*lnln/x={C*ll/x:.3f}  C*(lnln-1)/x={C*(ll-1)/x:.3f} t={time.time()-t:.0f}s", flush=True)

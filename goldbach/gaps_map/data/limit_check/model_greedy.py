import numpy as np, math, sys, time
from greedy_real import primes_upto

rng = np.random.default_rng(12345)
P = primes_upto(30_000_000)

def piQ(Q):
    return int(np.searchsorted(P, Q, side='right'))   # includes 2; fine

def model_greedy(x, Q, order='inc', nmax_direct=60000):
    """Poisson model of the greedy: uncovered count U; modulus s has s classes (0..s-1)
    each holding Poisson(U/s) rows, independently; take the largest. Class 0 holds ~nothing but ignore."""
    U = piQ(Q) - 1
    odd = P[(P >= 3) & (P <= x)]
    mods = odd if order == 'inc' else odd[::-1]
    for s in mods:
        if U <= 0: return True
        m = U / (s - 1)
        k = int(rng.poisson(m, size=s - 1).max()) if s <= nmax_direct else _max_poisson(m, s - 1)
        U -= max(k, 1)
    return U <= 0

def _max_poisson(m, n):
    # sample max of n iid Poisson(m): invert cdf^n at a uniform
    u = rng.random()
    t = -math.expm1(math.log(u) / n)          # tail prob target: P(max>=k+1)... use P(X>k) <= t
    # smallest k with P(X>k) <= t  (so that F(k)^n >= u approx)
    k = int(m)
    # tail by summation of pmf in log space
    def sf(k):  # P(X>k)
        # sum from k+1
        tot = 0.0
        j = k + 1
        lp = -m + j * math.log(m) - math.lgamma(j + 1)
        p = math.exp(lp)
        while True:
            tot += p
            j += 1
            p *= m / j
            if p < 1e-18 * tot or j > k + 10000: break
        return tot
    while sf(k) > t: k += 1
    while k > 0 and sf(k - 1) <= t: k -= 1
    return k

def D_model(x, order='inc', reps=3, tol=0.01):
    lx = math.log(x); base = x * lx * lx
    def ok(Q):
        return all(model_greedy(x, Q, order) for _ in range(reps))
    lo = 0.2 * base; hi = 2.0 * base
    while not ok(lo): lo *= 0.7
    while ok(hi): hi *= 1.4
    while hi / lo > 1 + tol:
        mid = math.sqrt(lo * hi)
        if ok(mid): lo = mid
        else: hi = mid
    return lo

if __name__ == '__main__':
    for x in [int(a) for a in sys.argv[1:]]:
        t = time.time()
        D = D_model(x)
        lx = math.log(x)
        print(f"model x={x} D={D:,.0f} D/(x ln^2 x)={D/(x*lx*lx):.3f} lnln={math.log(lx):.3f} t={time.time()-t:.1f}s", flush=True)

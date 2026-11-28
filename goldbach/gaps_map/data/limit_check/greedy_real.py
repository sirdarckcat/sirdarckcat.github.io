import numpy as np, math, sys, time

def primes_upto(n):
    s = np.ones(n+1, dtype=bool); s[:2] = False; s[4::2] = False
    for i in range(3, int(n**0.5)+1, 2):
        if s[i]: s[i*i::2*i] = False
    return np.nonzero(s)[0]

def greedy_cover(rows, moduli):
    """rows: int64 array (odd primes <= Q). moduli: list of odd primes in processing order.
    returns (success, n_uncovered_left, n_moduli_used)"""
    U = rows
    for s in moduli:
        if U.size == 0:
            return True, 0
        r = U % s
        cnt = np.bincount(r, minlength=s)
        c = int(cnt.argmax())
        U = U[r != c]
    return U.size == 0, U.size

def D_greedy(x, order='inc', Qlo=None, Qhi=None, P=None, tol=0.01):
    odd = P[(P >= 3) & (P <= x)]
    moduli = list(odd) if order == 'inc' else list(odd[::-1])
    lx = math.log(x)
    base = x * lx * lx
    lo = (Qlo or 0.2) * base
    hi = (Qhi or 2.0) * base
    def ok(Q):
        rows = P[(P >= 3) & (P <= Q)]
        s, left = greedy_cover(rows, moduli)
        return s
    # ensure lo ok, hi fail
    while not ok(lo): lo *= 0.7
    while ok(hi): hi *= 1.4
    while hi / lo > 1 + tol:
        mid = math.sqrt(lo * hi)
        if ok(mid): lo = mid
        else: hi = mid
    return lo

if __name__ == '__main__':
    xs = [int(a) for a in sys.argv[2:]]
    order = sys.argv[1]
    P = primes_upto(20_000_000)
    for x in xs:
        t = time.time()
        D = D_greedy(x, order, P=P)
        lx = math.log(x)
        print(f"{order} x={x} D={D:,.0f} D/(x ln^2 x)={D/(x*lx*lx):.3f} lnln={math.log(lx):.3f} t={time.time()-t:.1f}s", flush=True)

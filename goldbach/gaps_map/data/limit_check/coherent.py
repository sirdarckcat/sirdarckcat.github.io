import numpy as np, math, sys, time
from greedy_real import primes_upto

P = primes_upto(60_000_000)

def greedy_on(rows, moduli):
    U = rows
    for s in moduli:
        if U.size == 0: return U
        r = U % s
        cnt = np.bincount(r, minlength=s)
        c = int(cnt.argmax())
        U = U[r != c]
    return U

def pipeline(x, Q, z, y, N1s, verbose=False):
    """coherent block (z,y] with class N1 mod t, greedy classes on the odd primes <= z, greedy on the top (y,x].
    N1 is chosen among N1s to minimise the rows left by the block. Returns (complete, rows after block, rows after small)."""
    rows = P[(P >= 3) & (P <= Q)]
    block = P[(P > z) & (P <= y)]
    # mark[n] = n has a prime factor in the block, for n <= max N1
    Nmax = max(N1s)
    mark = np.zeros(Nmax + 1, dtype=bool)
    for t in block:
        mark[t::t] = True
    best = None
    for N1 in N1s:
        left = rows[~mark[N1 - rows]]
        if best is None or left.size < best[1].size: best = (N1, left)
    N1, left = best
    small = P[(P >= 3) & (P <= z)]
    after_small = greedy_on(left, small)
    top = P[(P > y) & (P <= x)]
    final = greedy_on(after_small, top)
    return final.size == 0, left.size, after_small.size, N1, rows.size

def plain(x, Q):
    rows = P[(P >= 3) & (P <= Q)]
    odd = P[(P >= 3) & (P <= x)]
    return greedy_on(rows, odd).size == 0

if __name__ == '__main__':
    x = int(sys.argv[1]); fac = float(sys.argv[2])
    lx = math.log(x); Q = int(fac * x * lx * lx)
    print(f"x={x} Q={Q} (= {fac} x ln^2 x)  plain greedy complete: {plain(x, Q)}", flush=True)
    K = 300
    for yfrac in [1/8, 1/4, 1/2]:
        y = int(x * yfrac)
        for z in [20, 50, 100, 200, 500, 1000, 2000]:
            if z >= y: continue
            t = time.time()
            ok, nb, ns, N1, nrows = pipeline(x, Q, z, y, list(range(Q, Q + K)))
            rnd = nrows * math.log(z) / math.log(y)       # random-class block: fraction ln z / ln y
            print(f"  y=x/{int(1/yfrac)} z={z:5d}: rows {nrows}, left by block {nb} ({nb/nrows:.3f}; random block would leave {math.log(z)/math.log(y):.3f}), after small greedy {ns}, complete={ok}  [{time.time()-t:.1f}s]", flush=True)

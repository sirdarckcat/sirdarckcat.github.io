import math, sys, time
import numpy as np
from coherent import *

def D_struct(x, y, z, K=200, tol=0.01):
    lx = math.log(x); base = x * lx * lx
    def ok(Q):
        Q = int(Q)
        return pipeline(x, Q, z, y, list(range(Q, Q + K)))[0]
    lo, hi = 0.3 * base, 1.6 * base
    if not ok(lo): return 0.0
    while ok(hi): hi *= 1.3
    while hi / lo > 1 + tol:
        mid = math.sqrt(lo * hi)
        if ok(mid): lo = mid
        else: hi = mid
    return lo

if __name__ == '__main__':
    x = int(sys.argv[1]); lx = math.log(x); base = x * lx * lx
    t0 = time.time()
    print(f"x={x}: plain greedy D/(x ln^2 x) from earlier runs = see out_greedy_real", flush=True)
    best = (0, None)
    for yfrac in [1/4, 1/2, 3/4]:
        y = int(x * yfrac)
        for z in [10, 20, 50, 100, 200, 500]:
            D = D_struct(x, y, z)
            r = D / base
            if r > best[0]: best = (r, (yfrac, z))
            print(f"  y=x*{yfrac:.2f} z={z:4d}: D/(x ln^2 x) = {r:.3f}   [{time.time()-t0:.0f}s]", flush=True)
    print("best:", best)

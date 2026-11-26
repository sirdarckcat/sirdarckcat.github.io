import math, sys, time
import numpy as np
from greedy_real import primes_upto
P = primes_upto(70_000_000)

def surv_fraction(x, Q, z, y, K=50):
    """fraction of the odd primes <= Q left by a coherent block (z, y], N1 = Q + k (best of K) vs the random-class fraction ln z/ln y"""
    rows = P[(P >= 3) & (P <= Q)]
    block = P[(P > z) & (P <= y)]
    Nmax = Q + K
    mark = np.zeros(Nmax + 1, dtype=bool)
    for t in block: mark[t::t] = True
    best = min(int((~mark[N1 - rows]).sum()) for N1 in range(Q, Q + K))
    return best / rows.size, math.log(z) / math.log(y)

print("   x        Q          y        z    coherent  random(ln z/ln y)  ratio")
for x, Q in [(10**4, 610_000), (10**5, 9_000_000), (10**6, 40_000_000), (3_750_000, 60_000_000)]:
    y = x // 4
    best = None
    for z in [10, 20, 40, 80, 160, 320, 640, 1280, 2560]:
        if z >= y: continue
        fc, fr = surv_fraction(x, Q, z, y)
        r = fc / fr
        if best is None or r < best[0]: best = (r, z, fc, fr)
        if x == 3_750_000 and z in (320, 640): print(f"      (z={z}: coherent {fc:.3f} vs random {fr:.3f})")
    r, z, fc, fr = best
    print(f"{x:9d} {Q:11d} {y:9d} {z:6d}   {fc:.3f}     {fr:.3f}           {r:.3f}", flush=True)

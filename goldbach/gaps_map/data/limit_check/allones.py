import numpy as np, math
from greedy_real import primes_upto
P = primes_upto(20_000_000)
kappa = 0.741308
for x in [1000, 10000, 100000]:
    lx = math.log(x); y1 = x/lx; Q = 0.7*x*lx*lx
    rows = P[(P >= 3) & (P <= Q)]
    bulk = P[(P >= 3) & (P <= y1)]
    alive = rows.copy()
    for s in bulk:                       # all classes 1: strike q = 1 mod s
        alive = alive[alive % s != 1]
    ref = rows.size * np.prod([(s-2)/(s-1) for s in bulk])
    print(f"x={x}: rows={rows.size}  alive with all bulk classes = 1: {alive.size}   random bulk: {ref:.0f}   ratio {alive.size/ref:.2f}")

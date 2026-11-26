import numpy as np, math, sys
from greedy_real import primes_upto
P = primes_upto(20_000_000)
kappa = 0.741308
def bulk(x, Qfac, ycut):
    lx = math.log(x); Q = Qfac * x * lx * lx
    rows = P[(P >= 3) & (P <= Q)]
    odd = P[(P >= 3) & (P <= ycut)]
    U = rows
    for s in odd:
        r = U % s
        cnt = np.bincount(r, minlength=s)
        c = int(cnt.argmax())
        U = U[r != c]
    # random-bulk reference: expected survivors for a random nonzero class per modulus
    ref = rows.size * np.prod([(s-2)/(s-1) for s in odd])
    return rows.size, U.size, ref
print("   x       Q-rows   R_greedy_bulk  R_random(exact prod)  ratio   kappa*pi/ln(y)   ratio2")
for x in [300, 1000, 3000, 10000, 30000, 100000]:   # prime table stops at 2e7, so Q = 0.7 x ln^2 x must stay below it
    lx = math.log(x); y1 = x/lx
    n, U, ref = bulk(x, 0.7, y1)
    print(f"{x:7d} {n:9d} {U:10d} {ref:12.0f} {U/ref:8.3f} {kappa*n/math.log(y1):12.0f} {U/(kappa*n/math.log(y1)):8.3f}", flush=True)

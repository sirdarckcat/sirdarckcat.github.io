import numpy as np, math
from greedy_real import primes_upto
from topode3 import crit
P = primes_upto(20_000_000)
kappa = 0.741308
Dg = {2000:75756, 5000:248742, 10000:603063, 20000:1407096, 50000:4236727, 100000:9593899}
print("   x      D_g       rows   U0_real(after bulk)  C_ode   real/ODE  bulk gain g_b   D/(x ln^2 x)")
for x, Q in Dg.items():
    lx = math.log(x); y1 = x/lx
    rows = P[(P >= 3) & (P <= Q)]
    U = rows
    for s in P[(P >= 3) & (P <= y1)]:
        r = U % s; cnt = np.bincount(r, minlength=s); c = int(cnt.argmax()); U = U[r != c]
    ref = rows.size * np.prod([(s-2)/(s-1) for s in P[(P>=3)&(P<=y1)]])
    C = crit(float(x), iters=20)
    print(f"{x:7d} {Q:10,d} {rows.size:8d} {U.size:10d} {C:10.0f} {U.size/C:8.3f} {U.size/ref:8.3f} {Q/(x*lx*lx):8.3f}", flush=True)

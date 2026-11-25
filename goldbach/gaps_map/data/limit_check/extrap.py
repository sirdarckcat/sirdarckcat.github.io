import math
from math import log
from topode import li, pi_est
from topode3 import crit
kappa = 0.741308

def inv_pi(target):
    # solve li(Q) - li(2) = target for Q (Newton on log Q)
    Q = target * max(2.0, log(max(target, 3.0)))
    for _ in range(60):
        f = li(Q) - li(2) - target
        Q -= f * log(Q)
        if Q < 10: Q = 10
        if abs(f) < 1e-9 * target: break
    return Q

rows = []
for x in [2e3, 2e4, 1e5, 1e6, 1e9, 1e12, 1e15, 1e20, 1e30, 1e45, 1e60, 1e90, 1e120]:
    lx = log(x); ll = log(lx); y1 = x / lx
    C = crit(x, iters=22)
    out = []
    for g_b, f_t in [(0.73, 0.88), (1.0, 1.0)]:
        U0 = f_t * C
        piQ = U0 * log(y1) / (g_b * kappa)
        Q = inv_pi(piQ)
        out.append(Q / (x * lx * lx))
    cap_form = (1/kappa) / (ll - 1)    # leading formula 1.349/(lnln x - 1)
    print(f"x={x:8.0e} lnln={ll:5.2f}  C/x={C/x:.3f}   D/(x ln^2 x): calibrated(g_b=.73,f_t=.88)={out[0]:.3f}   model-only(g_b=1,f_t=1)={out[1]:.3f}   1.349/(lnln-1)={cap_form:.3f}   1.349/lnln={(1/kappa)/ll:.3f}", flush=True)

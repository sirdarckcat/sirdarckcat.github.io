import numpy as np, math, sys
from greedy_real import primes_upto
rng = np.random.default_rng(7)
P = primes_upto(20_000_000)

def run(x, Qfac, order='inc'):
    lx = math.log(x); Q = Qfac * x * lx * lx
    rows = P[(P >= 3) & (P <= Q)]
    odd = P[(P >= 3) & (P <= x)]
    U = rows; log = []
    for s in odd:
        if U.size == 0: break
        r = U % s
        cnt = np.bincount(r, minlength=s)
        c = int(cnt.argmax())
        # also record mean count over nonzero classes and max over nonzero classes
        log.append((int(s), U.size, int(cnt[c]), float(cnt[1:].mean()) if s > 1 else 0))
        U = U[r != c]
    return Q, rows.size, log, U.size

def model_max(m, n, reps=20):
    return np.mean([rng.poisson(m, size=n).max() for _ in range(reps)])

x = int(sys.argv[1]); Qfac = float(sys.argv[2])
Q, nrows, log, left = run(x, Qfac)
print(f"x={x} Q={Q:,.0f} rows={nrows} leftover={left}")
lx = math.log(x)
y1 = x / lx
kappa = 0.7413
print(f"R0 predicted after bulk (<= y1={y1:.0f}): {kappa*nrows/math.log(y1):.0f}")
# actual U at s just above y1
for s, U, k, mean in log:
    if s > y1:
        print(f"U after bulk = {U} (ratio to kappa*pi/ln y1: {U/(kappa*nrows/math.log(y1)):.3f})"); break
# compare top-phase k with model max of Poisson(U/(s-1)) over s-1 classes, at selected moduli
print("   s        U     k_real  k_poissonmax  ratio")
sel = [t for t in log if t[0] > y1]
import itertools
step = max(1, len(sel)//14)
tot_real = tot_mod = 0
for i, (s, U, k, mean) in enumerate(sel):
    mm = model_max(U/(s-1), s-1, reps=4) if s < 30000 else None
    tot_real += k; tot_mod += mm if mm else 0
    if i % step == 0:
        print(f"{s:6d} {U:8d} {k:6d} {mm:10.2f} {k/mm:8.3f}")
print("sum k_real over top =", tot_real, " sum model max =", round(tot_mod,1), " ratio", round(tot_real/tot_mod,3))

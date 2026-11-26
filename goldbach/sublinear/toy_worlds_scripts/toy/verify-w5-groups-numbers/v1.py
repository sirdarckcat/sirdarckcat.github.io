import math, numpy as np, sympy, time
from base import *
from math import log, exp
t0 = time.time()
# ---- D(z)
lnX = 200 * log(10)
def theta(z): return math.fsum(math.log(int(p)) for p in sympy.primerange(2, z + 1))
print("theta(463)", round(theta(463), 3), "lnX", round(lnX, 3))
for z in (467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 600, 700, 1000, 2000, 5000, 10**4, 10**5, 2*10**5, 10**6):
    print("D(%d) = %.3f" % (z, theta(z) - lnX), end="; ")
print()
# exact D for j=1..8 from P = M*T
for j in range(1, 9):
    T = prod(LATER[:j]); P = M * T
    # ln(P/X) via integer arithmetic
    D = log(P) - lnX
    print("j", j, "T", T, "D %.4f e^D %.4g e^(D/2) %.4g" % (D, exp(D), exp(D / 2)))
# ---- tables
dl = {r: dlt_table(r) for r in cprimes}
print("min dlt over all cover primes/classes:", min(int(d.min()) for d in dl.values()), "; zero-cost classes per prime != base:",
      [(r, [int(c) for c in np.nonzero(dl[r] == 0)[0] if c != cover[r]]) for r in cprimes if (dl[r] == 0).sum() > 1])
hit = {s: hit_table(s) for s in LATER[:30]}
print("max hits first 8 later:", [int(hit[s].max()) for s in LATER[:8]])
unc = [n0 - sum(int(hit[s].max()) for s in LATER[:j]) for j in range(1, 9)]
print("unconstrained optimum j=1..8:", unc)
# ---- level counts of the cover side: polynomial product truncated at degree 16
DEG = 17
poly = [1] + [0] * (DEG - 1)
for r in cprimes:
    cnt = np.bincount(dl[r][dl[r] < DEG], minlength=DEG)
    new = [0] * DEG
    for a in range(DEG):
        if poly[a]:
            for b in range(DEG - a):
                if cnt[b]: new[a + b] += poly[a] * int(cnt[b])
    poly = new
print("A[k] cover class vectors at cost exactly k:", poly[:8])
# later side level counts and predictions
def later_levels(j, deg=DEG):
    pl = [1] + [0] * (deg - 1)
    for s in LATER[:j]:
        d = hit[s].max() - hit[s]
        cnt = np.bincount(d[d < deg], minlength=deg)
        new = [0] * deg
        for a in range(deg):
            if pl[a]:
                for b in range(deg - a):
                    if cnt[b]: new[a + b] += pl[a] * int(cnt[b])
        pl = new
    return pl
for j in range(3, 9):
    T = prod(LATER[:j]); P = M * T
    pl = later_levels(j)
    tot = [sum(poly[a] * pl[k - a] for a in range(k + 1)) for k in range(DEG)]
    cum = np.cumsum(tot)
    cumA = np.cumsum(poly); cumL = np.cumsum(pl)
    print("j", j, "n(sigma)*X/P for sigma=0..8:", ["%.4g" % (int(c) * X / P) for c in cum[:9]])
    print("    lists cover<=s, later<=s:", [(int(cumA[s]), int(cumL[s])) for s in range(8)])
# ---- own-window brute force
ks = np.arange(K, dtype=np.int64)
tothits = np.zeros(K, dtype=np.int16)
print("own window brute force:")
for j, s in enumerate(LATER[:8], 1):
    cls = (N0 % s + ks * (M % s)) % s
    if j <= 2:
        T = prod(LATER[:j])
        if j == 1: mult = np.bincount(cls, minlength=s)
        else:
            c1 = (N0 % LATER[0] + ks * (M % LATER[0])) % LATER[0]
            mult = np.bincount(c1 * s + cls, minlength=T)
        print("   j", j, "class-vector multiplicities min/max", mult.min(), mult.max(), "K/T %.3f" % (K / T))
    tothits += hit[s][cls].astype(np.int16)
    mx = int(tothits.max())
    print("   j", j, "best first-order", n0 - mx, "members at best", int((tothits == mx).sum()), "mean hits %.2f" % tothits.mean(),
          "deficit counts vs unconstrained 0..6:", [int((tothits == (n0 - unc[j-1]) - d).sum()) for d in range(7)])
print("time %.1f" % (time.time() - t0))

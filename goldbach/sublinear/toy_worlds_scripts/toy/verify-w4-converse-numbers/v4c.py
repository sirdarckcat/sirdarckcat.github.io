import math, random, numpy as np, flint
from vlib import *
cov, rows = get(); N0, M, K0 = win(cov); P = lp(467, 5000); random.seed(777)
def cert(sl, lists, K):
    el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]; ell = [K] + [L for a, d, L in lists]; n = len(ell)
    big = max(ell) << 40; w = [big // l for l in ell]
    R = [[w[0]] + [e * w[i + 1] for i, e in enumerate(el)]] + [[0] * (i + 1) + [s * w[i + 1]] + [0] * (len(sl) - i - 1) for i, s in enumerate(sl)]
    A = flint.fmpz_mat(R).lll()
    tau = [sum(abs(int(A[i, j])) for i in range(n)) / w[j] / ell[j] for j in range(n)]
    if max(tau) >= 1: return float('inf'), tau
    return math.prod(1 + 2 * t for t in tau) / math.prod(1 - t for t in tau), tau
print("n  median least lnE/n   median Hadamard ln(1/gm tau)   min over reps of [lnE + ln work]/n at that c")
for n in (2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 30, 40):
    m = n - 1; sl = P[:m]; cs = []; hs = []; fl = []
    for rep in range(5):
        lists = [(random.randrange(s), random.randrange(1, s), s // 2) for s in sl]; c = 0.5
        while True:
            E = math.exp(c * n); K = int(E * math.prod(s / L for s, (a, d, L) in zip(sl, lists))); f, tau = cert(sl, lists, K)
            if f <= math.e: break
            c += 0.05
        cs.append(c); hs.append(-sum(math.log(t) for t in tau) / n); fl.append(c + math.log(f) / n)
    print(n, "%.2f" % np.median(cs), "%.2f" % np.median(hs), "%.2f" % min(fl), flush=True)
# the real window with half-density lists: is there a certificate (any finite bound, and <= e)?
print("real window K, density 1/2 lists, 20 draws each: fraction with tau<1 everywhere, fraction with factor<=e, median factor")
for m in (1, 2, 3, 4, 5, 6):
    sl = P[:m]; fs = []
    for rep in range(20):
        lists = [(random.randrange(s), random.randrange(1, s), s // 2) for s in sl]; fs.append(cert(sl, lists, K0)[0])
    fs = np.array(fs); print(" m=%d n=%d lnE/n=%.2f finite %.2f <=e %.2f median factor %.3g" % (m, m + 1, (math.log(K0) - m * math.log(2)) / (m + 1), np.isfinite(fs).mean(), (fs <= math.e).mean(), np.median(fs)), flush=True)

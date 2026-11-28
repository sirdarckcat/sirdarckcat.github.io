import math, numpy as np, sympy
from vlib import *
cov, rows = get(); n = len(rows)
print("cover primes", len(cov), "max", max(cov), "all odd primes<=463 used:", sorted(cov) == list(sympy.primerange(3, 464)))
print("rows", n, "rows<=463", rows[rows <= 463])
# Prop C
sift = [q for q in range(465, Q, 2) if all((q % r) != 0 and (q % r) != a for r, a in cov.items())]
print("sifted", len(sift), "equal", sift == [int(x) for x in rows[rows > 463]])
print("rows mod 6:", set(int(x) for x in rows % 6), "classes mod 30:", len(set(int(x) for x in rows % 30)), "mod 210:", len(set(int(x) for x in rows % 210)), "mod 2310:", len(set(int(x) for x in rows % 2310)))
print("a3,a5,a7,a11", cov[3], cov[5], cov[7], cov[11])
print("n/Q", n / Q, "6n/Q", 6 * n / Q, "(5n/Q)/ln6", 5 * n / Q / math.log(6), "x0.0243", 5 * n / Q / math.log(6) * 0.0243)
P = lp(467, 5000); print("later primes", len(P))
st = {}
for s in P:
    t = tab(rows, s).astype(float); m = t.mean(); v = t.var()
    z = int((t == 0).sum())
    pin = (t.max() - m) / math.log(s)
    # thin: exclude empties
    thin = (n / (s - z) - m) / math.log(s / (s - z)) if z else 0
    srt = np.sort(t)[::-1]; best = 0
    cs = np.cumsum(srt)
    j = np.arange(1, s)
    fr = ((cs[:-1] / j - m) / np.log(s / j)).max()
    st[s] = (m, v / m, t.max(), z / s, pin, thin, fr, v)
for lo, hi in ((467, 600), (600, 1000), (1000, 2000), (2000, 3500), (3500, 5000), (467, 5000)):
    a = np.array([st[s] for s in P if lo <= s < hi])
    print(lo, hi, len(a), "mean %.3f var/mean %.4f +- %.4f max %.2f empty %.3f pin %.3f thin %.3f free %.3f" % (a[:,0].mean(), a[:,1].mean(), a[:,1].std()/math.sqrt(len(a)), a[:,2].mean(), a[:,3].mean(), a[:,4].mean(), a[:,5].mean(), a[:,6].mean()))
t = tab(rows, 467); print("467: max", t.max(), "mean", t.mean(), "rate", (t.max() - t.mean()) / math.log(467), t.max() / math.log(467))
# variance shares
allp = lp(467, Q); var = {s: tab(rows, s).var() for s in allp}
ex = sum(var.values())
# tail Q..1e8: sum over actual primes (segmented) of n/s(1-n/s)
tail = 0.0
import sympy
lo = Q
sv = sympy.sieve
# use numpy segmented sieve
def primes_seg(a, b):
    lim = int(b ** .5) + 1; base = np.array(list(sympy.primerange(2, lim + 1)))
    seg = np.ones(b - a, dtype=bool)
    for p in base:
        st0 = max(p * p, (a + p - 1) // p * p); seg[st0 - a::p] = False
    return np.nonzero(seg)[0] + a
a = Q
while a < 10 ** 8:
    b = min(a + 10 ** 7, 10 ** 8); pr = primes_seg(a, b).astype(float); tail += float(np.sum(n / pr * (1 - n / pr))); a = b
tot = ex + tail
print("var 467..Q %.2f tail(exact primes) %.2f total %.2f sd %.2f" % (ex, tail, tot, math.sqrt(tot)))
for hi in (509, 1000, 2000, 5000, 20000, 200000):
    print(hi, "%.2f%%" % (100 * sum(v for s, v in var.items() if s <= hi) / tot))
N0, M, K = win(cov)
print("digits M", len(str(M)), "lnM %.3f" % math.log(M), "K", K, "log2 %.3f lnK %.3f" % (math.log2(K), math.log(K)), "N0 even", N0 % 2 == 0, "cover ok", all(N0 % r == a for r, a in cov.items()))
print("467*479", 467 * 479, "467*479*487", 467 * 479 * 487)
big = lp(467, K // 467 + 1); exs = {s: (lambda t: (t.max() - t.mean(), t.max()))(tab(rows, s)) for s in big}
best = max(((exs[s][0] + exs[s2][0], s, s2) for i, s in enumerate(big) for s2 in big[i + 1:] if s * s2 <= K and s < 4700))
print("best pair", best, exs[best[1]], exs[best[2]])
# D = ln(P/K)
for m in (3, 4, 5, 6, 8, 10):
    print(m, "%.2f" % (sum(math.log(s) for s in P[:m]) - math.log(K)))

# Lemma L: for a probability vector pi on m >= 2 points,  ln m * (sum pi^2 - 1/m) <= ln m - H(pi) = KL(pi || uniform).
# Reduction (convex/concave argument): the maximiser of sum phi(pi_c), phi(x) = -x ln x + ln m x^2, has the form (a, b, ..., b).
import numpy as np, math, random
worst = -1e9; arg = None
def gap(m, a):
    b = (1 - a) / (m - 1)
    H = -(a * np.log(a) + np.where(b > 0, (m - 1) * b * np.log(np.where(b > 0, b, 1)), 0))
    return (math.log(m) - H) - math.log(m) * (a * a + (m - 1) * b * b - 1 / m)   # must be >= 0
ms = list(range(2, 3000)) + [int(10 ** x) for x in np.linspace(3.5, 12, 200)]
mn = 1e9
for m in ms:
    t = np.concatenate([np.linspace(0, 1, 4001)[1:], 10.0 ** np.linspace(-9, 0, 2000)])
    a = np.unique(np.concatenate([1 / m + (1 - 1 / m) * t, 1 - (1 - 1 / m) * 10.0 ** np.linspace(-12, 0, 2000)]))
    a = a[(a > 1 / m) & (a <= 1)]
    g = gap(m, a)
    # relative to the gain, to see the margin
    if g.min() < mn: mn = g.min(); arg = (m, a[g.argmin()])
print("one-parameter family: min of KL - gain over m in 2..3000 and to 1e12:", mn, "at", arg)
# random vectors, small m (sanity of the reduction)
rng = np.random.default_rng(1); mn2 = 1e9
for m in (2, 3, 4, 5, 7, 10, 30, 100, 467):
    for conc in (0.02, 0.1, 0.5, 1, 5):
        P = rng.dirichlet([conc] * m, size=20000)
        P = np.clip(P, 1e-300, 1)
        H = -(P * np.log(P)).sum(1)
        g = (math.log(m) - H) - math.log(m) * ((P * P).sum(1) - 1 / m)
        mn2 = min(mn2, g.min())
    # supports of size B, uniform
    for B in range(1, m + 1):
        g = (math.log(m) - math.log(B)) - math.log(m) * (1 / B - 1 / m)
        mn2 = min(mn2, g)
print("random Dirichlet vectors and uniform-on-B vectors: min of KL - gain:", mn2)
# page corollary (b) as stated: 'a place restricted to B classes adds at most d/|B| while costing ln(q^d/|B|); only |B| = 1 gives rate 1'
print("gross rate (ln m/|B|) / ln(m/|B|) for some (m,|B|):", {(m, B): round((math.log(m) / B) / math.log(m / B), 3) for m, B in ((4, 2), (4, 3), (5, 3), (5, 4), (9, 8), (25, 24), (467, 466), (467, 1), (467, 2))})
print("marginal rate ln m (1/B - 1/m) / ln(m/B):", {(m, B): round(math.log(m) * (1 / B - 1 / m) / math.log(m / B), 4) for m, B in ((4, 2), (4, 3), (5, 3), (5, 4), (9, 8), (25, 24), (467, 466), (467, 1), (467, 2))})

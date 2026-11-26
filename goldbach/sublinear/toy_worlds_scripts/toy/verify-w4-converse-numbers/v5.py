# exact-bracket DP for the tax table (verifier): lower = costs rounded up to the grid (feasible), upper = rounded down.
import math, numpy as np, itertools
from vlib import *
cov, rows = get(); N0, M, K = win(cov); P = lp(467, 5000)
cur = []
for s in P:
    t = np.sort(tab(rows, s))[::-1].astype(float); j = np.arange(1, s); g = np.cumsum(t)[:-1] / j - t.mean(); c = np.log(s / j)
    cur.append((s, g, c))
def dp(B, tax, delta, pins=False, up=True):
    nb = int(math.floor(B / delta + 1e-9)); f = np.zeros(nb + 1)
    for s, g, c in cur:
        if pins: g = g[:1]; c = c[:1]
        cc = c + tax
        L = np.ceil(cc / delta - 1e-12).astype(int) if up else np.floor(cc / delta + 1e-12).astype(int)
        # best (largest gain = smallest j) per level
        lv, first = np.unique(L, return_index=True)
        new = f.copy()
        for l, i in zip(lv, first):
            if l <= nb and g[i] > 0:
                if l == 0: new = np.maximum(new, f + g[i])
                else: np.maximum(new[l:], f[:nb + 1 - l] + g[i], out=new[l:])
        f = new
    return f[nb]
for B, delta in ((16.88, 0.01), (50.0, 0.02), (150.0, 0.05)):
    print("B =", B, "grid", delta, flush=True)
    for tax in (0.0, 0.25, 0.5, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0):
        lo = dp(B, tax, delta, up=True); hi = dp(B, tax, delta, up=False)
        print("   tax %.2f: optimum in [%.2f, %.2f]" % (tax, lo, hi), flush=True)
    lo = dp(B, 0.0, delta / 5, pins=True, up=True); hi = dp(B, 0.0, delta / 5, pins=True, up=False)
    print("   pins: optimum in [%.2f, %.2f]" % (lo, hi), flush=True)
# pins exact at ln K (pairs; triples impossible)
ex = [(g[0], s) for s, g, c in cur]
best = max((a[0] + b[0], a[1], b[1]) for a, b in itertools.combinations(ex, 2) if a[1] * b[1] <= K)
print("pins exact at lnK (pairs within 467..5000):", best, " best single:", max(ex))

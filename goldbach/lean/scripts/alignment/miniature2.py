"""Prize and anatomy of a miniature from the output of truth2.c (histograms of several slices are added up).
  python miniature2.py NAME PREFIX...          prints: the cover-first and ideal orders, the prize, and for tiers
                                               of best members the cover nats and luck nats (as in anatomy1.py)."""
import math, sys
import numpy as np
def load(prefixes):
    cnt = np.zeros((330, 330)); suc = np.zeros((330, 330))
    for p in prefixes:
        for line in open(p + ".hist"):
            a, b, c, s = map(int, line.split()); cnt[a, b] += c; suc[a, b] += s
    return cnt, suc
def examined(cn, cs, t):
    """N examined for t successes when levels are taken in increasing order, linear inside a level"""
    pn = ps = 0.0
    for lev in range(len(cn)):
        n2, s2 = pn + cn[lev], ps + cs[lev]
        if s2 >= t and s2 > ps: return pn + (n2 - pn) * (t - ps) / (s2 - ps)
        pn, ps = n2, s2
    return math.inf
if __name__ == "__main__":
    name = sys.argv[1]; cnt, suc = load(sys.argv[2:]); n = cnt.sum(); S = suc.sum()
    c1 = cnt.sum(axis=1); s1 = suc.sum(axis=1); c2 = cnt.sum(axis=0); s2 = suc.sum(axis=0)
    k1 = np.arange(330)
    m1 = (c1 * k1).sum() / n; m2 = (c2 * k1).sum() / n
    print(f"# {name}: members {int(n):,d}, successes {int(S):,d} (one in e^{math.log(n / S):.2f}); rows left at the line: least {int(np.nonzero(c1)[0][0])}, mean {m1:.2f}, sd {math.sqrt((c1 * (k1 - m1) ** 2).sum() / n):.2f}; "
          f"at full depth: least {int(np.nonzero(c2)[0][0])}, mean {m2:.2f}, sd {math.sqrt((c2 * (k1 - m2) ** 2).sum() / n):.2f}")
    print("successes wanted | N examined, cover first | ideal | prize, nats")
    for t in (1, 3, 10, 30, 100, 300, 1000, 3000):
        if t > S: break
        a = examined(c1, s1, t); b = examined(c2, s2, t)
        print(f"{t} | {a:,.0f} | {b:,.0f} | {math.log(a / b):.2f}")
    print("tier (rows left at full depth at most) | members | rarity | cover nats | luck nats | rows left at the line in the tier: mean | cover-first quantile of the tier's median")
    cum1 = np.cumsum(c1); pa = c1 / n
    for t in range(int(np.nonzero(c2)[0][0]), int(np.nonzero(c2)[0][0]) + 9):
        h = cnt[:, :t + 1].sum(axis=1); T = h.sum()
        if T == 0: continue
        p = h / T; ok = p > 0; cover = float((p[ok] * np.log(p[ok] / pa[ok])).sum()); rar = math.log(n / T)
        med = int(np.searchsorted(np.cumsum(h), T / 2)); q = (cum1[med - 1] + 0.5 * c1[med]) / n
        print(f"{t} | {int(T):,d} | {rar:.2f} | {cover:.2f} | {rar - cover:.2f} | {(p * k1).sum():.2f} | {q:.4%}")

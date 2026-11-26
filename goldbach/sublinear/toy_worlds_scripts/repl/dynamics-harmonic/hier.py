#!/usr/bin/env python3
"""(a) the hierarchy across covers.  Level r = the class of N modulo r.  For every cover prime r, with the other 88 classes
as in the real cover: rows left as a function of the class of r (the sub-windows of the 88-prime cover), the variance that
level carries, the gain of the best class over a flat scan of the 88-prime window, per nat of room.  Then the three top
levels 449, 457, 463 jointly (9.5e7 sub-windows of the 86-prime cover), and the later primes as the continuation."""
import math, numpy as np
from common import setup, cover
import cover_record as cr
cov, rows, N0, M, K = setup(); Q = 200000; PR = cr.PR[cr.PR < Q]; lam = 0.024 * (36.5 / (0.024 * 1502))   # exponent per row: 36.5 nats / 1502 rows
lam = 36.5 / 1502
print(f"exponent per row {lam:.5f} nats")
def left_without(drop):
    alive = np.ones(len(PR), bool)
    for r, a in cov:
        if r not in drop: alive &= (PR % r) != a
    return PR[alive]
print("level r | rows of the (cover minus r) | rows left: best class (the cover's? ) | mean over classes | sd over classes | flat scan of all classes: ln mean exp(-lam rows) as rows-equivalent | gain of best class over flat, nats | room ln r | nats per nat")
tot = 0; totroom = 0; res = []
for r, a in cov:
    base = left_without({r}); f = np.bincount(base % r, minlength=r); left = len(base) - f
    flat = -math.log(np.mean(np.exp(-lam * (left - left.min())))) / lam + left.min()       # rows-equivalent of a flat scan over the classes
    gain = lam * (flat - left.min()); res.append((r, len(base), left.min(), left[a], left.mean(), left.std(), flat, gain))
    tot += gain; totroom += math.log(r)
for x in res[:6] + res[-6:]:
    r = x[0]; print(f"  {r} | {x[1]} | {x[2]} (cover's class leaves {x[3]}) | {x[4]:.1f} | {x[5]:.2f} | {x[6]:.1f} | {x[7]:+.3f} | {math.log(r):.2f} | {x[7]/math.log(r):.4f}")
print(f"  cover's class is the best class at {sum(1 for x in res if x[2] == x[3])} of {len(res)} levels; sum of single-level gains {tot:.2f} nats for {totroom:.1f} nats of room ({tot/totroom:.4f} per nat)")
g = np.array([x[7] for x in res]); rr = np.array([x[0] for x in res]); 
for lo, hi in ((3, 50), (50, 150), (150, 300), (300, 464)):
    s = (rr >= lo) & (rr < hi); print(f"  levels {lo}..{hi}: {int(s.sum())} primes, gain {g[s].sum():.2f} nats, room {np.log(rr[s]).sum():.1f}, {g[s].sum()/np.log(rr[s]).sum():.4f} per nat")
# three top levels jointly
base = left_without({449, 457, 463}); n86 = len(base); fs = [np.bincount(base % r, minlength=r) for r in (449, 457, 463)]
# first-order distribution of rows struck = f1+f2+f3 (overlaps: a row counted twice when two classes hold it; at most one row per pair of classes since 449*457 > Q)
h = np.array([1.0])
for f in fs: h = np.convolve(h, np.bincount(f) / len(f))
struck = np.arange(len(h)); mean = (h * struck).sum(); sd = math.sqrt((h * struck ** 2).sum() - mean ** 2)
best = sum(int(f.max()) for f in fs); cur = n86 - len(rows)
flat = -math.log((h * np.exp(lam * (struck - mean))).sum()) / lam     # rows-equivalent shift of the flat scan relative to the mean
print(f"86-prime cover: {n86} rows; the 449*457*463 = {449*457*463:.3e} sub-windows strike (first order) mean {mean:.2f} sd {sd:.2f} rows; the real cover's three classes strike {cur}; best classes separately {best}")
print(f"  share of sub-windows striking >= {cur} rows (first order): {h[struck >= cur].sum():.3e}; flat scan of the 86-prime window = mean + {-flat:.2f} rows; best sub-window gains {lam*(cur-mean+flat):+.3f} nats over the flat scan and uses {math.log(449*457*463):.1f} nats less room")
print("continuation below the cover (later primes; these levels cost members of the window): r | best class strikes | mean | gain nats (first order, exponent per row) | per nat")
for r in (467, 479, 487, 491, 499, 503, 509, 997, 1999, 4999, 9973, 99991):
    f = np.bincount(rows % r, minlength=r); gain = lam * (f.max() - f.mean()) ; print(f"  {r} | {f.max()} | {f.mean():.2f} | {gain:+.3f} | {gain/math.log(r):.4f}")

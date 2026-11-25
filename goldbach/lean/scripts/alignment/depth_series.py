"""The prize as a function of the depth, on one exact miniature: true successes, the exact histogram with the chance
(1 - p)^k for a member with k rows left at that depth, and the histogram of random class vectors with the same chance.
  python depth_series.py LINE DEPTH:EXACT_PREFIX:ENSEMBLE_PREFIX ...      (prefixes of the merged .hist files)"""
import math, sys
import numpy as np
from miniature2 import load, examined
LINE = int(sys.argv[1]); k = np.arange(330)
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
print("depth | primes beyond the line | rows left: mean +- sd | correlation with the cover | chance p of a row left | members with rarity about 11 nats: exact / ensemble | prize at 100 successes: true | exact histogram | ensemble | at 1,000: true | exact histogram | ensemble | at 3,000: true | exact histogram | ensemble")
for arg in sys.argv[2:]:
    z, ex, en = arg.split(":"); z = int(z); cnt, suc = load([ex]); ens, _ = load([en]); n = cnt.sum(); m = ens.sum(); S = suc.sum(); sc = n / m
    c1 = cnt.sum(axis=1); c2 = cnt.sum(axis=0); e2 = ens.sum(axis=0); s2 = suc.sum(axis=0)
    m1 = (c1 * k).sum() / n; m2 = (c2 * k).sum() / n; v1 = (c1 * (k - m1) ** 2).sum() / n; v2 = (c2 * (k - m2) ** 2).sum() / n
    r = float(((k[:, None] - m1) * (k[None, :] - m2) * cnt).sum() / n) / math.sqrt(v1 * v2)
    lev = np.nonzero(c2)[0]
    def nll(p):
        q = (1 - p) ** lev; return -float((s2[lev] * np.log(q) + (c2[lev] - s2[lev]) * np.log1p(-q)).sum())
    ps = np.linspace(0.05, 0.7, 6501); p = float(ps[np.argmin([nll(x) for x in ps])]); wgt = (1 - p) ** k
    cum = np.cumsum(c2); t11 = int(np.searchsorted(cum, n * math.exp(-11.3)))          # level whose cumulative count is about e^-11.3 of the members
    tail = f"{int(cum[t11]):,d} / {np.cumsum(e2)[t11] * sc:,.0f} = {cum[t11] / (np.cumsum(e2)[t11] * sc):.3f}"
    mc = cnt * wgt[None, :]; me = ens * sc * wgt[None, :]; cols = []
    for t in (100, 1000, 3000):
        for c, s in ((cnt, suc), (cnt, mc), (ens * sc, me)):
            cols.append(math.log(examined(c.sum(axis=1), s.sum(axis=1), t) / examined(c.sum(axis=0), s.sum(axis=0), t)))
    nl = len([q for q in primes_upto(z) if q > LINE])
    print(f"{z} | {nl} | {m2:.2f} +- {math.sqrt(v2):.2f} | {r:.3f} | {p:.4f} | {tail} | " + " | ".join(f"{x:.2f}" for x in cols))

"""Family 4 in its best form: one table indexed by the residue of N modulo 29*31*37*41 (1.36 million buckets, which
fits a second-level cache), holding for every bucket the incidences of its four classes with the rows; a second table
modulo 43*47*53*59 (6.3 million buckets) for the eight-prime version.  Members of the best covers are looked up (one
reduction and one probe per table) and kept when   rows left at depth 23 - lambda x (bucket value - average) <= theta,
i.e. a member of a worse cover is kept only from a better bucket.  The kept members are scored at depth 200.

Work = (members looked up) x 2 x tables / 90  +  members kept.  The members looked up are all those with at most
c_max rows left at depth 23, c_max the largest level from which anything is kept."""
import math, sys
import numpy as np
import pp
from classes import DEEP, W
from refcurve import cover_order, gains, cells

N = np.asarray(pp.N); k1 = np.asarray(pp.K1); k2 = np.asarray(pp.K2); su = np.asarray(pp.SUCC)
ORDER = cover_order(); OPS_PER_UNIT = 90.0
LEVEL = np.bincount(k1, minlength=64); CUM = np.cumsum(LEVEL)
def cap(idx):
    kk = k2[idx]; return int(su[idx].sum()), int((kk <= 9).sum()), int((kk <= 10).sum()), int((kk <= 12).sum())
print("tables | lambda | members kept | largest rows left at depth 23 looked up | members looked up | work | successes (cover-first prefix of equal work) | rows left at depth 200 <= 9 (same) | <= 10 (same) | <= 12 (same) | "
      "N examined for 1 | 3 | 10 | 30 | gain in nats over cover first at 1 | 3 | 10 | 30 | the same gains for the cover-first prefix of equal work")
for ntab, T in ((1, DEEP[:4]), (2, DEEP[:8])):
    v = np.zeros(len(N), dtype=np.int16); CH = 1 << 24
    for a in range(0, len(N), CH):
        n = N[a:a + CH].astype(np.int64); t = np.zeros(len(n), dtype=np.int64)
        for s in T: t += W[s][n % s]
        v[a:a + CH] = t
    mean = float(v.mean()); rng = np.random.default_rng(11); noise = rng.random(len(N), dtype=np.float32) * 1e-3
    for lam in (0.1, 0.2, 0.3, 0.5, 0.8):
        key = k1.astype(np.float32) - np.float32(lam) * (v.astype(np.float32) - np.float32(mean)) + noise
        big = 3000000
        part = np.argpartition(key, big)[:big]; part = part[np.argsort(key[part], kind="stable")]
        for Wsel in (10000, 30000, 100000, 300000, 1000000, 3000000):
            idx = np.sort(part[:Wsel]); cmax = int(k1[idx].max()); looked = int(CUM[cmax])
            work = looked * 2 * ntab / OPS_PER_UNIT + Wsel
            ridx = np.sort(np.asarray(ORDER[:int(round(work))]))
            ex = pp.examined(k2[idx], su[idx]); rex = pp.examined(k2[ridx], su[ridx])
            c = cap(idx); r = cap(ridx); d = {"examined": ex, "gain": gains(ex)}; rd = {"gain": gains(rex)}
            print(f"{ntab} | {lam} | {Wsel:,d} | {cmax} | {looked:,d} | {work:,.0f} | {c[0]} ({r[0]}) | {c[1]} ({r[1]}) | {c[2]} ({r[2]}) | {c[3]} ({r[3]}) | "
                  f"{cells(d)} | {cells(d, 'gain', '{:+.2f}')} | {cells(rd, 'gain', '{:+.2f}')}", flush=True)

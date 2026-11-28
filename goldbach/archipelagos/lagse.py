# Block-bootstrap error of the measured archipelago enrichment R(d), averaged over a lag class, compared
# with the model (sieve to 997, independent survivors) evaluated on the same N.  usage: python3 lagse.py NAME
import sys
import numpy as np
from lib import *
name = sys.argv[1]
meta, g, isp, spf = load(name)
L = meta["L"]; G = thresholds(g)[0]; big = g >= G; rq = rows_below(G); rset = set(int(q) for q in rq)
R = rough(spf, 997); c = float(np.asarray(isp).sum() / R.sum()); lc = np.log1p(-c)
LM = 6_000_000; u = count_rows(R, meta, rq, LM + 2000).astype(np.float64)
BL = 50_000; nb = LM // BL; rng = np.random.default_rng(3)
classes = {"0 mod 6, d < G": [d for d in range(6, G, 6)][:40], "2 mod 6, d < G": [d for d in range(8, G, 6)][:40],
           "4 mod 6, d < G": [d for d in range(4, G, 6)][:40], "0 mod 6, G < d < 2G": [d for d in range(G + 6 - G % 6, 2 * G, 6)][:40]}
for tag, lags in classes.items():
    jb = np.zeros(nb); pa = np.zeros(nb); pb = np.zeros(nb); mj = np.zeros(nb); ma = np.zeros(nb); mb = np.zeros(nb)
    for d in lags:
        j = d // 2
        x = big[:LM]; yv = big[j:j + LM]
        sh = np.zeros(LM, dtype=np.int16)
        for q in rq:
            if q + d in rset: sh += row_view(R, meta, q, LM)
        a = np.exp(lc * u[:LM]); b = np.exp(lc * u[j:j + LM]); jt = np.exp(lc * (u[:LM] + u[j:j + LM] - sh))
        blk = lambda v: v.reshape(nb, BL).sum(1)
        jb += blk((x & yv).astype(np.float64)); pa += blk(x.astype(np.float64)); pb += blk(yv.astype(np.float64))
        mj += blk(jt); ma += blk(a); mb += blk(b)
    def stat(sel):
        meas = jb[sel].sum() * BL * len(sel) / (pa[sel].sum() * pb[sel].sum()) * 1.0
        mod = mj[sel].sum() * BL * len(sel) / (ma[sel].sum() * mb[sel].sum())
        return meas / mod
    full = stat(np.arange(nb))
    bs = [stat(rng.integers(0, nb, nb)) for _ in range(400)]
    print(f"{name} {tag:<22} {len(lags):>2} lags: measured / model = {full:.3f}  (+-2se {2*np.std(bs):.3f})")

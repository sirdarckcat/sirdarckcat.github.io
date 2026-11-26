# Data for the charts (one JSON): lag curve, calibration, map around the window record.
import json
import numpy as np
from lib import *
name = "e18"
meta, g, isp, spf = load(name)
L, N0, lo = meta["L"], meta["N0"], meta["lo"]
G = thresholds(g)[0]; big = g >= G; rq = rows_below(G); rset = set(int(q) for q in rq)
R = rough(spf, 997); c = float(np.asarray(isp).sum() / R.sum()); lc = np.log1p(-c)
LM = 1_500_000
u = count_rows(R, meta, rq, LM + 2000).astype(np.float64)
lag = []
for d in range(2, G + 120, 2):
    j = d // 2
    meas = (big[:-j] & big[j:]).mean() / (big[:-j].mean() * big[j:].mean())
    sh = np.zeros(LM, dtype=np.int16)
    shq = [q for q in rq if q + d in rset]
    for q in shq: sh += row_view(R, meta, q, LM)
    a = np.exp(lc * u[:LM]); b = np.exp(lc * u[j:j + LM]); jt = np.exp(lc * (u[:LM] + u[j:j + LM] - sh))
    lag.append(dict(d=d, measured=round(float(meas), 3), model=round(float(jt.mean() / (a.mean() * b.mean())), 3), shared=len(shq)))
uf = count_rows(R, meta, rq)
cal = []
for k in range(0, 36):
    m = uf == k
    if m.sum() >= 200: cal.append(dict(u=k, n=int(m.sum()), observed=float(big[m].mean()), model=float((1 - c) ** k)))
# map around the window record
i0 = int(g.argmax()); W = 900
sl = slice(max(0, i0 - W), min(L, i0 + W))
cs = np.concatenate([[0], np.cumsum(np.asarray(isp), dtype=np.int64)])
ii = np.arange(sl.start, sl.stop)
a_hi = N0 - lo - 3 + 2 * ii; a_lo = N0 - lo - G + 2 * ii
Pw = (cs[a_hi + 1] - cs[a_lo])
amap = dict(N_start=int(N0 + 2 * sl.start), step=2, g=g[sl].tolist(), primes_below=Pw.tolist(), G=G,
            record_N=int(N0 + 2 * i0), record_g=int(g[i0]), mean_primes_below=float((cs[N0 - lo - 3 + 2 * np.arange(0, L, 97) + 1] - cs[N0 - lo - G + 2 * np.arange(0, L, 97)]).mean()))
json.dump(dict(name=name, G=G, c997=c, lag=lag, calibration=cal, record_map=amap), open("viz_e18.json", "w"))
print("lags", len(lag), "max |meas-model|/model:", max(abs(r["measured"] - r["model"]) / r["model"] for r in lag))
print("record N", amap["record_N"], "g", amap["record_g"], "big N in map:", int(sum(1 for v in amap["g"] if v >= G)), "of", len(amap["g"]))

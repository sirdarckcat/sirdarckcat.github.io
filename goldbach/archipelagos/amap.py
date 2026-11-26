# g(N) and the count of primes just below N along a stretch containing the largest archipelago at 1e18
import json
import numpy as np
from lib import *
meta, g, isp, spf = load("e18")
L, N0, lo = meta["L"], meta["N0"], meta["lo"]
G = thresholds(g)[0]
A = json.load(open("archipelagos_e18.json"))["largest"][0]
i_start = (A["N_min"] - N0) // 2; i_end = i_start + A["span"] // 2
pad = 350
sl = slice(i_start - pad, i_end + pad)
ii = np.arange(sl.start, sl.stop)
cs = np.concatenate([[0], np.cumsum(np.asarray(isp), dtype=np.int64)])
Pw = cs[N0 - lo - 3 + 2 * ii + 1] - cs[N0 - lo - G + 2 * ii]
samp = np.arange(0, L, 101)
meanP = float((cs[N0 - lo - 3 + 2 * samp + 1] - cs[N0 - lo - G + 2 * samp]).mean())
out = dict(N_start=int(N0 + 2 * sl.start), g=g[sl].tolist(), primes_below=Pw.tolist(), G=G, mean_primes_below=meanP,
           archipelago=dict(N_min=A["N_min"], span=A["span"], size=A["size"], gmax=A["gmax"]))
json.dump(out, open("amap_e18.json", "w"))
gb = g[sl] >= G
print("stretch", len(ii), "even N; big in stretch:", int(gb.sum()), "; primes below: mean in stretch for big N %.1f vs window mean %.1f; min %d" % (Pw[gb].mean(), meanP, Pw.min()))

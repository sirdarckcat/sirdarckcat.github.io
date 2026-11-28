# Is the sub-Poisson occupancy explained by capacity?  For each class c of a large prime r, the survivors are the m_c targets
# of that class thinned with the survival probability p = prod_{r in A}(1 - 1/(r-1)).  Model 'thinned': n_c ~ Binomial(m_c, p);
# model 'balls': n_c ~ Poisson(|S|/(r-1)).  Compared with the measured classes holding >= 2, 3, 4 survivors (t1_x100000.json).
import json, math, numpy as np, t1
from scipy.stats import binom, poisson
x = 100000; d = json.load(open("t1_x100000.json")); lnx = math.log(x)
P = t1.primes_upto(int(8 * x * lnx) + 2)
for wt in ("x/2", "x^0.9"):
    W = d["w"][wt]; w = W["w"]; A = P[P <= w]; B = P[(P > w) & (P <= x)]
    p = float(np.prod(1 - 1 / (A.astype(float) - 1)))
    for C in ("1.35", "4.0"):
        a = W["A"][C]; T = P[P <= float(C) * x * lnx]
        thin = {2: 0.0, 3: 0.0, 4: 0.0}
        for r in B.tolist():                                   # all large primes: histogram of class sizes m_c
            m = np.bincount(np.bincount(T % r, minlength=r)[1:])  # nonzero classes
            for k in thin: thin[k] += float((m * binom.sf(k - 1, np.arange(len(m)), p)).sum())
        print(f"w={wt:6} C={C:4}: classes with >= 2 / 3 / 4 survivors, measured {a['c2']:.0f} / {a['c3']:.0f} / {a['c4']:.0f}; "
              f"thinned targets {thin[2]:.0f} / {thin[3]:.0f} / {thin[4]:.0f}; balls {a['c2_pois']:.0f} / {a['c3_pois']:.0f} / {a['c4_pois']:.0f}")

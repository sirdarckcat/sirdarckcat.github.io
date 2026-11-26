# explicit feasible solutions (traceback) at the real budget, checked from scratch
import math, numpy as np
from vlib import *
cov, rows = get(); N0, M, K = win(cov); P = lp(467, 5000); B = math.log(K); delta = 0.01
def solve(tax):
    nb = int(B / delta); f = np.zeros(nb + 1); choice = []
    for s in P:
        t = np.sort(tab(rows, s))[::-1].astype(float); j = np.arange(1, s); g = np.cumsum(t)[:-1] / j - t.mean(); c = np.log(s / j) + tax
        L = np.ceil(c / delta - 1e-12).astype(int); lv, first = np.unique(L, return_index=True)
        new = f.copy(); ch = np.zeros(nb + 1, dtype=np.int32)       # 0 = unused, else j
        for l, i in zip(lv, first):
            if 0 < l <= nb and g[i] > 0:
                cand = f[:nb + 1 - l] + g[i]; better = cand > new[l:] + 1e-12
                new[l:][better] = cand[better]; ch[l:][better] = i + 1
        f = new; choice.append(ch)
    # traceback
    b = nb; sol = []
    for idx in range(len(P) - 1, -1, -1):
        jj = int(choice[idx][b])
        if jj:
            s = P[idx]; sol.append((s, jj)); b -= int(math.ceil((math.log(s / jj) + tax) / delta - 1e-12))
    return sol
for tax in (1.0, 1.5, 1.8, 2.0, 2.2):
    sol = solve(tax); gain = 0; cost = 0
    for s, j in sol:
        t = np.sort(tab(rows, s))[::-1]; gain += t[:j].mean() - t.mean(); cost += math.log(s / j) + tax
    print("tax %.1f: lists (prime, classes) %s  total cost %.3f <= %.3f  gain %.2f rows  (pins 13.10) -> %+.3f nats" % (tax, sol, cost, B, gain, (gain - 13.0992) * 0.0243))

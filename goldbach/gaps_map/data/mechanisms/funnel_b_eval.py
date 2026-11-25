import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
from funnel import load_sub
from funnel_b import ev, V
cfg = {'B': (36, (30, 27, 25, 23, 19)), 'C': (35, (27, 25, 23, 21, 17))}
for nm in sys.argv[1:]:
    k1max, thr = cfg[nm]; k, s, m = load_sub(nm, k1max); K1 = 64; k1 = k[:, 0].astype(np.int64)
    cg = np.bincount(k1, minlength=K1) * V; sg = np.bincount(k1[s == 1], minlength=K1); msk = cg > 0
    base = cost_levels(cg[msk], sg[msk], KS); e = ev(k, s, thr)
    print(nm, 'thr', thr, 'retained', int(e[2].sum()), 'of', int(s.sum()), 'mean cost %.1f units' % (e[1].sum() / e[3].sum()))
    print('  gain ln(base/funnel) under (V):', {t: round(math.log(base[t] / e[0][t]), 2) for t in KS}, flush=True)
    del k, s

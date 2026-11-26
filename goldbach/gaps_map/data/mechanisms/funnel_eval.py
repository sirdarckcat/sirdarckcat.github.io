import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
from funnel import eval_policy, load_sub
cfg = {'B': (36, (30, 27, 25, 23)), 'C': (35, (27, 25, 23, 21)), 'A': (36, (30, 27, 25, 23))}
for nm in sys.argv[1:]:
    k1max, thr = cfg[nm]; k, s, m = load_sub(nm, k1max)
    base = eval_policy(k, s, (99, 99, 99, 99))[0]; e = eval_policy(k, s, thr)
    print(nm, 'subset', len(k), 'successes', int(s.sum()), 'thr', thr, 'retained', int(e[2].sum()), 'mean cost/member %.3f' % (e[1].sum() / e[3].sum()))
    print('  baseline E:', {t: round(v) for t, v in base.items()}); print('  funnel   E:', {t: round(v) for t, v in e[0].items()})
    print('  gain ln(base/funnel):', {t: round(math.log(base[t] / e[0][t]), 2) for t in KS}, flush=True)
    del k, s

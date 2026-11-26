import numpy as np, sys, math, itertools, time
sys.path.insert(0, '.')
from lib import *
# cumulative mod-op costs after depth checkpoints 31,43,61,97,199 (odd primes 31..d), in units of 36 ops
OPS = np.array([1, 4, 8, 15, 36]) / 36.0
def load_sub(nm, k1max):
    m = Mini(nm); k = np.asarray(m.k); s = np.asarray(m.s)
    sel = np.flatnonzero(k[:, 0] <= k1max)
    return k[sel].copy(), s[sel].copy(), m
def policy_cost(k, thr):
    """per-member cost (units) and pass flag. thr = (t31, t43, t61, t97); k columns: 23,31,43,61,97,199"""
    alive = np.ones(len(k), dtype=bool); cost = np.zeros(len(k))
    for j in range(5):
        cost += np.where(alive, OPS[j] - (OPS[j - 1] if j else 0.0), 0.0)
        if j < 4: alive &= k[:, j + 1] <= thr[j]
    return cost, alive
def eval_policy(k, s, thr, K1=64, targets=KS):
    cost, alive = policy_cost(k, thr); k1 = k[:, 0].astype(np.int64)
    cg = np.bincount(k1, weights=cost, minlength=K1); sg = np.bincount(k1, weights=(alive & (s == 1)).astype(float), minlength=K1)
    ng = np.bincount(k1, minlength=K1)
    o = np.arange(K1); msk = ng > 0
    return cost_levels(cg[msk], sg[msk].astype(np.int64), targets), cg, sg, ng, alive
if __name__ == '__main__':
    t0 = time.time(); k, s, m = load_sub('A', 36); print('A subset', len(k), 'succ', int(s.sum()), round(time.time() - t0, 1), 's', flush=True)
    base = eval_policy(k, s, (99, 99, 99, 99))[0]; print('baseline (cover first, 1 unit/member):', {t: round(v) for t, v in base.items()})
    # coordinate descent on thresholds
    def obj(thr):
        e = eval_policy(k, s, thr)[0]
        return sum(math.log(e[t]) for t in (10, 30, 100) if not math.isnan(e[t])) if all(not math.isnan(e[t]) for t in (10, 30, 100)) else 1e9
    med = [np.median(k[::50, j]) for j in (1, 2, 3, 4)]; print('median k at depths 31..97', med)
    thr = [int(med[0]) + 6, int(med[1]) + 6, int(med[2]) + 6, int(med[3]) + 6]; best = obj(thr)
    for rnd in range(3):
        for j in range(4):
            for d in range(-8, 9):
                cand = list(thr); cand[j] = thr[j] + d; v = obj(cand)
                if v < best - 1e-9: best, thr = v, cand
        print('round', rnd, thr, round(best, 3), round(time.time() - t0), 's', flush=True)
    e = eval_policy(k, s, thr)
    print('funnel thr', thr, 'cost-to-k (units):', {t: round(v) for t, v in e[0].items()})
    print('gain ln(base/funnel):', {t: round(math.log(base[t] / e[0][t]), 2) for t in KS})
    print('mean cost per member (units):', e[1].sum() / e[3].sum(), ' successes retained', int(e[2].sum()), 'of', int(s.sum()))
    np.save('funnel_thr.npy', np.array(thr))

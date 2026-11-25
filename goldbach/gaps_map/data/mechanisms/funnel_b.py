# Funnel under verification-priced accounting: sieve stages cost OPS/36 units; a member that passes all thresholds is verified at V units (2.2 modexp x 139 units/modexp).
import numpy as np, sys, math, time
sys.path.insert(0, '.')
from lib import *
from funnel import load_sub, OPS
V = 2.2 * 139.0
def pol(k, thr):
    alive = np.ones(len(k), dtype=bool); cost = np.zeros(len(k))
    for j in range(5):
        cost += np.where(alive, OPS[j] - (OPS[j - 1] if j else 0.0), 0.0)
        alive &= k[:, j + 1] <= thr[j]
    cost += np.where(alive, V, 0.0); return cost, alive
def ev(k, s, thr, K1=64):
    cost, alive = pol(k, thr); k1 = k[:, 0].astype(np.int64)
    cg = np.bincount(k1, weights=cost, minlength=K1); sg = np.bincount(k1, weights=(alive & (s == 1)).astype(float), minlength=K1); msk = np.bincount(k1, minlength=K1) > 0
    return cost_levels(cg[msk], sg[msk].astype(np.int64), KS), cg, sg, np.bincount(k1, minlength=K1), alive
if __name__ == '__main__':
    nm = sys.argv[1]; k1max = int(sys.argv[2]); k, s, m = load_sub(nm, k1max)
    k1 = k[:, 0].astype(np.int64); K1 = 64; cg = np.bincount(k1, minlength=K1) * V; sg = np.bincount(k1[s == 1], minlength=K1); msk = cg > 0
    base = cost_levels(cg[msk], sg[msk], KS); print(nm, 'baseline (verify every member, V=%.0f units):' % V, {t: round(v) for t, v in base.items()}, flush=True)
    def obj(thr):
        e = ev(k, s, thr)[0]
        return sum(math.log(e[t]) for t in (10, 30, 100)) if all(not math.isnan(e[t]) for t in (10, 30, 100)) else 1e9
    thr = [30, 27, 25, 23, 21]; best = obj(thr); t0 = time.time()
    for rnd in range(3):
        for j in range(5):
            for d in (-6, -4, -3, -2, -1, 1, 2, 3):
                c = list(thr); c[j] += d; v = obj(c)
                if v < best - 1e-9: best, thr = v, c
        print('round', rnd, thr, round(best, 3), round(time.time() - t0), 's', flush=True)
    e = ev(k, s, thr); print('thr', thr, 'cost-to-k:', {t: round(v) for t, v in e[0].items()}); print('gain ln(base/funnel):', {t: round(math.log(base[t] / e[0][t]), 2) for t in KS})
    print('mean cost per member %.2f units; successes retained %d of %d' % (e[1].sum() / e[3].sum(), int(e[2].sum()), int(s.sum())))
    np.save(f'funnel_b_thr_{nm}.npy', np.array(thr))

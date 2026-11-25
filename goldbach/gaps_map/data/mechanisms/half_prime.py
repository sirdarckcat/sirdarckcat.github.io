import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
cfg = {'A': 10**9, 'B': 2 * 10**9, 'C': 10**9}
for nm in sys.argv[1:]:
    X = cfg[nm]; n = X // 2 + 2; comp = np.zeros(n, dtype=bool); comp[:2] = True
    for p in range(2, int(n ** .5) + 1):
        if not comp[p]: comp[p * p::p] = True
    m = Mini(nm); idx = np.asarray(m.idx); s = np.asarray(m.s); k1 = np.asarray(m.k[:, 0]).astype(np.int64); K1 = 64
    ip = ~comp[idx]                      # N/2 prime
    cnt_all = np.bincount(k1, minlength=K1); cnt_ip = np.bincount(k1[ip], minlength=K1)
    sc_all = np.bincount(k1[s == 1], minlength=K1); sc_ip = np.bincount(k1[(s == 1) & ip], minlength=K1)
    print(nm, 'density of N/2 prime among allowed: %.4f ; successes with N/2 prime: %d of %d (expected %.1f at same k1 mix)' % (ip.mean(), sc_ip.sum(), sc_all.sum(), (sc_all * cnt_ip / np.maximum(cnt_all, 1)).sum()))
    # ordering: members with N/2 prime first within k1; and family-only cover-first
    key = k1 * 2 + (~ip).astype(np.int64); cnts = np.bincount(key, minlength=2 * K1); scs = np.bincount(key[s == 1], minlength=2 * K1); skey = key[s == 1]
    kk = np.arange(2 * K1) // 2; sig_b = kk.astype(float); sig_m = kk * 10.0 + (np.arange(2 * K1) % 2)
    pt, bs, pb, pm = gain_boot(cnts, scs, skey, sig_b, sig_m, B=200); print('  order (k1, N/2 prime first):', fmt(pt, bs))
    # family-only: scan only members with N/2 prime
    c2 = cnts.copy(); c2[1::2] = 0
    sc2 = scs.copy(); sc2[1::2] = 0; pf = cost_from(c2, sc2, sig_b); pbb = cost_from(cnts, scs, sig_b)
    print('  family-only (N/2 prime) cover-first E:', {t: round(v) if not np.isnan(v) else None for t, v in pf.items()}, 'vs all:', {t: round(v) for t, v in pbb.items()})
    del comp

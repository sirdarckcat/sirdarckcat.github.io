# M5: neighbourhood of perfect squares (N within Q above/below a square), with credit for rows forced composite by the factorisation (m-a)(m+a).
# needs fam_sq.u32 (fam_gen.py) and fam_sq.out (evalN) and pop_A.npz (fam.py)
import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import cost_levels, KS
P = np.load('pop_A.npz'); mu = P['mu']; cnt = P['cnt']; cal = float(P['cal']); sumP = P['sumP']
dt = np.dtype([('idx', '<u4'), ('k1', 'u1'), ('k199', 'u1'), ('f23', 'u1'), ('f199', 'u1'), ('coh', 'u1'), ('s', 'u1'), ('p0', 'u1'), ('p1', 'u1')])
r = np.fromfile('fam_sq.out', dtype=dt); rho = 0.5; k1 = r['k1'].astype(int); K1 = 64
Pf = np.power(1 - rho, r['k199'].astype(float)); Pf2 = np.power(1 - rho, (r['k199'].astype(int) - r['f199'].astype(int)).astype(float))
n_f = np.bincount(k1, minlength=K1).astype(float); s_f1 = cal * np.bincount(k1, weights=Pf, minlength=K1); s_f2 = cal * np.bincount(k1, weights=Pf2, minlength=K1)
def ci(n, s):
    msk = n > 0; return cost_levels(n[msk], s[msk], KS)
base = ci(cnt.astype(float), cal * sumP); f2 = ci(n_f, s_f2)
fm = lambda d: {t: (None if np.isnan(v) else round(v)) for t, v in d.items()}
print('members', len(r), 'observed successes in family', int(r['s'].sum()))
print('k1-matched mean-P ratio: no forcing credit %.3f ; with forced-row credit %.3f' % (Pf.sum() / mu[k1].sum(), Pf2.sum() / mu[k1].sum()))
print('forced rows alive at depth 23: %.2f, at depth 199: %.3f per member' % (r['f23'].mean(), r['f199'].mean()))
print('population cover-first (predicted mass):', fm(base)); print('squares family, forced credit            :', fm(f2))
print('gain (neg = worse):', {t: (None if np.isnan(f2[t]) else round(math.log(base[t] / f2[t]), 2)) for t in KS})
dens = len(r) / cnt.sum(); print('density %.4f, cost %.2f nats, nats per kill %.1f' % (dens, -math.log(dens), -math.log(dens) / r['f199'].mean()))

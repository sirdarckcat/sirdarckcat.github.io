import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
P = np.load('pop_A.npz'); mu = P['mu']; cnt = P['cnt']; cal = float(P['cal']); sumP = P['sumP']
Q = 1000; m = Mini('A'); K1 = 64
BS = {'{31,37,41}': 31 * 37 * 41, '{31,37,41,43}': 31 * 37 * 41 * 43, '{31,37,41,43,47}': 31 * 37 * 41 * 43 * 47}
acc = {b: dict(n=np.zeros(K1), s=np.zeros(K1), sp=np.zeros(K1), obs=0, mu=0.0) for b in BS}
for a in range(0, m.M, CH):
    b = min(a + CH, m.M); N = np.asarray(m.idx[a:b]).astype(np.int64) * 2; kk = np.asarray(m.k[a:b]); s = np.asarray(m.s[a:b]); k1 = kk[:, 0].astype(np.int64)
    P199 = np.power(0.5, kk[:, 5].astype(np.float64))
    for nm, Mp in BS.items():
        r = N % Mp; sel = (r > Q) & (r <= 2 * Q)
        d = acc[nm]; d['n'] += np.bincount(k1[sel], minlength=K1); d['sp'] += cal * np.bincount(k1[sel], weights=P199[sel], minlength=K1); d['obs'] += int(s[sel].sum())
        d['mu'] += mu[k1[sel]].sum()
print('coherent block family: members with N mod prod(B) in (Q,2Q]  (the same small integer t is the residue at every prime of B)')
base = None
for nm, d in acc.items():
    n = d['n'].sum(); dens = n / cnt.sum(); ratio = (d['sp'].sum() / cal) / d['mu']
    print(f' B={nm}: members {int(n)} density {dens:.4f} (cost {-math.log(dens):.2f} nats); k1-matched mean-P ratio {ratio:.3f} (ln {math.log(ratio):+.3f}); predicted successes {d["sp"].sum():.2f}, observed {d["obs"]}')

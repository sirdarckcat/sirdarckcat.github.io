import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
fn = sys.argv[1] if len(sys.argv) > 1 else 'bayesA.bin'
NBIN = 800; a = np.fromfile(fn, dtype=np.int64).reshape(64, NBIN, 2); cnt = a[:, :, 0].reshape(-1); suc = a[:, :, 1].reshape(-1)
kk = np.arange(64 * NBIN) // NBIN; bn = np.arange(64 * NBIN) % NBIN; L = (bn + 0.5) / 40.0 - 14.0
sk = np.repeat(np.arange(64 * NBIN), suc)
print('members', cnt.sum(), 'successes', suc.sum(), 'k1 range', kk[cnt > 0].min(), kk[cnt > 0].max())
tg = (1, 3, 10, 30)
sig_b = kk.astype(float); sig_m = kk * 1000.0 - bn
pt, bs, pb, pm = gain_boot(cnt, suc, sk, sig_b, sig_m, B=300, targets=tg)
print('observed-success gain of the Bayes-optimal shallow ordering (any function of N mod 3..23), MC noise makes this a lower bound:')
print(' ', fmt(pt, bs, tg)); print('  baseline E:', {t: round(v) for t, v in pb.items()}, ' Bayes-ordered E:', {t: round(v) for t, v in pm.items()})
# model-based: predicted mass exp(L) per member, calibrated to the observed total
w = np.exp(L); cal = suc.sum() / (cnt * w).sum(); sp = cnt * w * cal
eb = cost_from(cnt, sp, sig_b, tg); em = cost_from(cnt, sp, sig_m, tg)
print('model-predicted gain (upper estimate, includes winner-curse from MC noise):', {t: round(math.log(eb[t] / em[t]), 2) for t in tg})
# spread of L within the best k1 groups
for k1 in (27, 29, 31, 33):
    c = cnt.reshape(64, NBIN)[k1]; Lb = ((np.arange(NBIN) + 0.5) / 40.0 - 14.0)
    if c.sum() == 0: continue
    mu = (c * Lb).sum() / c.sum(); sd = math.sqrt((c * (Lb - mu) ** 2).sum() / c.sum()); print(' k1=%d: members %d, L mean %.2f sd %.3f (includes MC noise)' % (k1, c.sum(), mu, sd))

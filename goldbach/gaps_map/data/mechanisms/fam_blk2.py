import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
nm = sys.argv[1]; Q = int(sys.argv[2]); m = Mini(nm); K1 = 64
sumP = np.zeros(K1); cnt = np.zeros(K1, dtype=np.int64); obs = np.zeros(K1)
for a in range(0, m.M, CH):
    b = min(a + CH, m.M); kk = np.asarray(m.k[a:b]); k1 = kk[:, 0].astype(np.int64)
    sumP += np.bincount(k1, weights=np.power(0.5, kk[:, 5].astype(float)), minlength=K1); cnt += np.bincount(k1, minlength=K1); obs += np.bincount(k1, weights=np.asarray(m.s[a:b]), minlength=K1)
cal = obs.sum() / sumP.sum(); mu = np.where(cnt > 0, sumP / np.maximum(cnt, 1), 0.0)
Mp = 31 * 37 * 41; n = 0; sp = 0.0; muS = 0.0; ob = 0; ncomp = 0
for a in range(0, m.M, CH):
    b = min(a + CH, m.M); N = np.asarray(m.idx[a:b]).astype(np.int64) * 2; kk = np.asarray(m.k[a:b]); k1 = kk[:, 0].astype(np.int64)
    r = N % Mp; sel = (r > Q) & (r <= 2 * Q); n += sel.sum(); sp += cal * np.power(0.5, kk[sel, 5].astype(float)).sum(); muS += mu[k1[sel]].sum(); ob += int(np.asarray(m.s[a:b])[sel].sum())
print(nm, 'B={31,37,41}: members', n, 'density %.4f' % (n / cnt.sum()), 'predicted successes %.2f (k1-matched %.2f), observed %d' % (sp, cal * muS, ob), 'ln ratio %.3f' % math.log(sp / (cal * muS)))

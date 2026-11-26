import math, numpy as np
from vlib import *
cov, rows = get(); rng = np.random.default_rng(424242)
FR = (2, 3, 4, 6, 8, 12, 16, 32, 64)
def best(t):
    s = len(t); m = t.mean(); out = np.zeros((len(FR), 4))
    hi = np.full(len(FR), -1); lo = np.full(len(FR), 10 ** 9)
    Ls = [max(2, s // f) for f in FR]
    D = np.arange(1, (s - 1) // 2 + 1)
    for blk in np.array_split(D, max(1, len(D) // 256)):
        idx = (blk[:, None] * np.arange(s)[None, :]) % s
        u = t[idx]                               # u[d, i] = t(d i)
        uu = np.concatenate([u, u], axis=1); c = np.concatenate([np.zeros((len(blk), 1), dtype=np.int64), np.cumsum(uu, axis=1)], axis=1)
        for i, L in enumerate(Ls):
            w = c[:, L:L + s] - c[:, 0:s]
            hi[i] = max(hi[i], w.max()); lo[i] = min(lo[i], w.min())
    for i, L in enumerate(Ls):
        gh = hi[i] / L - m; gt = (t.sum() - lo[i]) / (s - L) - m
        out[i] = (gh, gh / math.log(s / L), gt, gt / (-math.log(1 - L / s)))
    return out
P = lp(467, 5000); sel = [s for s in P if s < 1000] + [s for s in P if s >= 1000][::4]
R = []; U = []
for s in sel:
    t = tab(rows, s); R.append(best(t)); U.append(best(rng.permutation(t)))
R = np.array(R); U = np.array(U); S = np.array(sel); print(len(sel), "primes")
for lo, hi in ((467, 1000), (1000, 2000), (2000, 5000), (467, 5000)):
    k = (S >= lo) & (S < hi); print(lo, hi, k.sum())
    for i, f in enumerate(FR):
        if f in (2, 4, 8, 16, 64):
            r = R[k, i].mean(0); u = U[k, i].mean(0); print("  1/%d heavy gain %.4f/%.4f rate %.4f/%.4f | thin gain %.4f/%.4f rate %.4f/%.4f" % (f, r[0], u[0], r[1], u[1], r[2], u[2], r[3], u[3]))
    br = R[k][:, :, 1].max(1); bu = U[k][:, :, 1].max(1); tr = R[k][:, :, 3].max(1); tu = U[k][:, :, 3].max(1)
    print("  best heavy rate %.4f/%.4f diff %+.4f +- %.4f ; thin %.4f/%.4f diff %+.4f +- %.4f" % (br.mean(), bu.mean(), (br - bu).mean(), (br - bu).std() / math.sqrt(k.sum()), tr.mean(), tu.mean(), (tr - tu).mean(), (tr - tu).std() / math.sqrt(k.sum())))
    d2 = R[k, 0, 0] - U[k, 0, 0]; print("  density 1/2 gain excess %+.4f +- %.4f" % (d2.mean(), d2.std() / math.sqrt(k.sum())))

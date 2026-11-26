import math, numpy as np
from vlib import *
cov, rows = get(); N0, M, K = win(cov); rng = np.random.default_rng(5150)
P = lp(467, 2000); m = len(P); T = [tab(rows, s) for s in P]; iu = np.triu_indices(m, 1)
def zwin(tabs):
    zs = []
    for w in range(16):
        k = np.arange(w << 20, (w << 20) + (1 << 17), dtype=np.int64); X = np.empty((1 << 17, m), dtype=np.float32)
        for i, s in enumerate(P): X[:, i] = tabs[i][(N0 % s + (M % s) * (k % s)) % s]
        X -= X.mean(0); X /= np.sqrt((X.astype(np.float64) ** 2).sum(0)).astype(np.float32)
        R = (X.T @ X).astype(np.float64); zs.append(R[iu] * math.sqrt(1 << 17))
    return np.array(zs)
zr = zwin(T); print("real rms %.4f max %.2f n>3 %d n>4 %d" % (math.sqrt((zr ** 2).mean()), abs(zr).max(), (abs(zr) > 3).sum(), (abs(zr) > 4).sum()), flush=True)
w, p = np.unravel_index(np.argmax(abs(zr)), zr.shape); print("max at window", w, "pair", P[iu[0][p]], P[iu[1][p]], "z in all windows for this pair:", np.round(zr[:, p], 2))
# pairs by product size
prod = np.array([P[i] * P[j] for i, j in zip(*iu)])
for lo, hi in ((0, 2 ** 18), (2 ** 18, 2 ** 19), (2 ** 19, 2 ** 20), (2 ** 20, 2 ** 21), (2 ** 21, 2 ** 23)):
    k = (prod >= lo) & (prod < hi); print("  product in [%d,%d): pairs %d rms %.3f frac|z|>3 %.5f" % (lo, hi, k.sum(), math.sqrt((zr[:, k] ** 2).mean()), (abs(zr[:, k]) > 3).mean()))
for rep in range(5):
    zs = zwin([rng.permutation(t) for t in T]); print("shuf rms %.4f max %.2f n>3 %d n>4 %d" % (math.sqrt((zs ** 2).mean()), abs(zs).max(), (abs(zs) > 3).sum(), (abs(zs) > 4).sum()), flush=True)
    if rep == 0:
        for lo, hi in ((0, 2 ** 18), (2 ** 18, 2 ** 19), (2 ** 19, 2 ** 20), (2 ** 20, 2 ** 21), (2 ** 21, 2 ** 23)):
            k = (prod >= lo) & (prod < hi); print("  shuf product in [%d,%d): rms %.3f frac|z|>3 %.5f" % (lo, hi, math.sqrt((zs[:, k] ** 2).mean()), (abs(zs[:, k]) > 3).mean()))

import math, numpy as np
from vlib import *
cov, rows = get(); n = len(rows); N0, M, K = win(cov); rng = np.random.default_rng(99)
S = np.load("S_all.npy"); P = lp(467, 2000); m = len(P)
T = [tab(rows, s) for s in P]
def gram(k0, cnt, tabs):
    k = np.arange(k0, k0 + cnt, dtype=np.int64); X = np.empty((cnt, m), dtype=np.float64)
    for i, s in enumerate(P): X[:, i] = tabs[i][(N0 % s + (M % s) * (k % s)) % s]
    return X
# (a) 2^22 members
KK = 1 << 22; CH = 1 << 17; G = np.zeros((m, m)); g1 = np.zeros(m)
for c0 in range(0, KK, CH):
    X = gram(c0, CH, T); g1 += X.sum(0); G += X.T @ X
mu = g1 / KK; C = G / KK - np.outer(mu, mu); sd = np.sqrt(np.diag(C)); Rm = C / np.outer(sd, sd); iu = np.triu_indices(m, 1); z = Rm[iu] * math.sqrt(KK)
print("(a) pairs", len(z), "mean z %.4f rms %.4f max|z| %.2f" % (z.mean(), math.sqrt((z ** 2).mean()), abs(z).max()))
tv = sum(t.var() for t in T); print("    Var(S) 2^22 %.3f / tables %.3f = %.5f" % (S[:KK].astype(float).var(), tv, S[:KK].astype(float).var() / tv))
# (b) sums of top members, exact over all ordered pairs
H = 1 << 21; S1 = S[:H].astype(float); thr = np.quantile(S1, 0.99); A = (S1 >= thr); top = np.nonzero(A)[0]
print("(b) top", len(top), "thr", thr, "mean top %.2f all(2^22) %.3f sd %.2f" % (S1[top].mean(), S[:KK].mean(), S[:KK].astype(float).std()))
F = np.fft.rfft(A.astype(float), 2 * H); c = np.rint(np.fft.irfft(F * F, 2 * H))   # c[j] = #ordered pairs k1+k2=j
c2 = c.copy(); c2[2 * top] -= 1                                                    # remove k1==k2
tot = c2.sum(); mean_pair = (c2 * S[:2 * H]).sum() / tot
# sd of S among pair sums
v_pair = (c2 * (S[:2 * H].astype(float) - mean_pair) ** 2).sum() / tot
print("    all %d ordered pairs k1!=k2: mean S(k1+k2) %.4f ; mean all members(window) %.4f ; excess %+.4f ; sd S over pairs %.2f ; naive se for 4e5 %.3f" % (tot, mean_pair, S.astype(float).mean(), mean_pair - S[:KK].mean(), math.sqrt(v_pair), math.sqrt(v_pair / 4e5)))
# distinct sums count -> effective sample size
print("    distinct values of k1+k2:", int((c2 > 0).sum()))
d = S[2 * top].astype(float); print("    S(2k1): mean %.3f excess %+.3f se %.3f" % (d.mean(), d.mean() - S[:KK].mean(), d.std() / math.sqrt(len(d))))
# also differences k1-k2 (adversarial extra) and top-top+top
# (c) 2^17 windows, real vs shuffled
def zwin(tabs):
    zs = []
    for w in range(16):
        X = gram(w * (1 << 20), 1 << 17, tabs); R = np.corrcoef(X.T); zs.append(R[iu] * math.sqrt(1 << 17))
    zs = np.array(zs); return math.sqrt((zs ** 2).mean()), abs(zs).max(), int((abs(zs) > 3).sum()), zs.size
print("(c) 2^17 windows real:", zwin(T))
for rep in range(2): print("    shuffled tables:", zwin([rng.permutation(t) for t in T]))

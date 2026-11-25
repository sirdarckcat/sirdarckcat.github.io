"""The small-work rows of bucket_soft.py (one table on 29, 31, 37, 41, lambda = 0.1) repeated over 8 random tie-breaks,
against the cover-first prefix of equal work with the same 8 tie-breaks: mean and standard deviation of the counts of
best members captured.  The only randomness is the order inside a level of equal score."""
import numpy as np
import pp
from classes import DEEP, W
N = np.asarray(pp.N); k1 = np.asarray(pp.K1); k2 = np.asarray(pp.K2); su = np.asarray(pp.SUCC)
CUM = np.cumsum(np.bincount(k1, minlength=64))
v = np.zeros(len(N), dtype=np.int16); CH = 1 << 24
for a in range(0, len(N), CH):
    n = N[a:a + CH].astype(np.int64); t = np.zeros(len(n), dtype=np.int64)
    for s in DEEP[:4]: t += W[s][n % s]
    v[a:a + CH] = t
mean = float(v.mean()); lam = 0.1; WS = (10000, 30000, 100000, 300000)
def cap(idx):
    kk = k2[idx]; return np.array([su[idx].sum(), (kk <= 9).sum(), (kk <= 10).sum(), (kk <= 12).sum()], dtype=float)
acc = {W_: ([], []) for W_ in WS}
for rep in range(8):
    rng = np.random.default_rng(1000 + rep); noise = rng.random(len(N), dtype=np.float32) * 1e-3
    key = k1.astype(np.float32) - np.float32(lam) * (v.astype(np.float32) - np.float32(mean)) + noise
    part = np.argpartition(key, WS[-1])[:WS[-1]]; part = part[np.argsort(key[part], kind="stable")]
    key0 = k1.astype(np.float32) + noise
    part0 = np.argpartition(key0, 2 * WS[-1])[:2 * WS[-1]]; part0 = part0[np.argsort(key0[part0], kind="stable")]
    for W_ in WS:
        idx = part[:W_]; work = int(round(int(CUM[int(k1[idx].max())]) * 2 / 90.0 + W_))
        acc[W_][0].append(cap(idx)); acc[W_][1].append(np.append(cap(part0[:work]), work))
print("members kept | work | table: successes | <= 9 rows left at depth 200 | <= 10 | <= 12 | cover-first prefix of equal work: successes | <= 9 | <= 10 | <= 12   (mean +- sd over 8 tie-breaks) | ratio table / prefix for <= 10 | <= 12 | in nats")
for W_ in WS:
    a = np.array(acc[W_][0]); b = np.array(acc[W_][1])
    f = lambda x, i: f"{x[:, i].mean():.1f} +- {x[:, i].std():.1f}"
    r10 = a[:, 2].mean() / b[:, 2].mean(); r12 = a[:, 3].mean() / b[:, 3].mean()
    print(f"{W_:,d} | {b[:, 4].mean():,.0f} | {f(a,0)} | {f(a,1)} | {f(a,2)} | {f(a,3)} | {f(b,0)} | {f(b,1)} | {f(b,2)} | {f(b,3)} | {r10:.3f} | {r12:.3f} | {np.log(r10):+.3f}, {np.log(r12):+.3f}", flush=True)

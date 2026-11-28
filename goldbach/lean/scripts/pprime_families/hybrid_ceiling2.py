"""As hybrid_ceiling.py, with the robust measure: how many of the best members (rows left at depth 200 <= 9, 10, 12) and
of the 256 successes are among the W best by the mixed score.  lambda = 0 is the cover-first prefix."""
import numpy as np
import pp
k1 = np.asarray(pp.K1).astype(np.float32); k2 = np.asarray(pp.K2); su = np.asarray(pp.SUCC)
inc = np.load("data/inc_deep.npy").astype(np.float32)
WS = (10000, 30000, 100000, 300000, 1000000, 3000000, 10000000)
print("lambda | W | successes | rows left at depth 200 <= 9 (401 in all) | <= 10 (1,965) | <= 12 (33,598)   [mean of 4 random tie-breaks]")
for lam in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5):
    acc = {W: np.zeros(4) for W in WS}
    for rep in range(4):
        rng = np.random.default_rng(100 + rep); noise = rng.random(len(k1), dtype=np.float32) * 1e-3
        key = k1 - np.float32(lam) * (inc - np.float32(75.0)) + noise
        part = np.argpartition(key, WS[-1])[:WS[-1]]
        part = part[np.argsort(key[part], kind="stable")]
        for W in WS:
            idx = part[:W]; kk = k2[idx]
            acc[W] += np.array([su[idx].sum(), (kk <= 9).sum(), (kk <= 10).sum(), (kk <= 12).sum()])
    for W in WS:
        a = acc[W] / 4
        print(f"{lam:.2f} | {W:>10,d} | {a[0]:6.1f} | {a[1]:6.1f} | {a[2]:7.1f} | {a[3]:8.1f}", flush=True)

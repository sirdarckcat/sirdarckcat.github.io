# Do the members selected for few survivors among the rows below the design level also have fewer survivors beyond it?  (Mechanism behind a heavier overshoot tail.)
# Whole window of 2e7 members, my 1,524-row cover split at 170,000: block 1 = alive rows below 170,000, block 2 = alive rows in [170,000, 200,000);
# strikes F1, F2 = rows of each block struck by the primes in (463, 4,000] (same residues N mod s for both blocks).  Correlation over the window and mean of F2 in the top 1% / 0.1% of F1.
import numpy as np, math, sys, time
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]; cls = np.load('../lattice/cls_sa_11.npy'); alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; R1 = R[R < 170000]; R2 = R[R >= 170000]; K = 20_000_000; zmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 5); ss = [int(s) for s in primes_upto(zmax) if s > 463]
print('rows: block 1 %d, block 2 %d; primes %d up to %d' % (len(R1), len(R2), len(ss), zmax), flush=True)
F1 = np.zeros(K, np.float32); F2 = np.zeros(K, np.float32); kk = np.arange(K, dtype=np.int64); t0 = time.time()
cov_th = 0.0; v1 = v2 = 0.0
for s in ss:
    c1 = np.bincount(R1 % s, minlength=s).astype(np.float64); c2 = np.bincount(R2 % s, minlength=s).astype(np.float64)
    a = int(rng.integers(s)); m = int(rng.integers(1, s)); idx = ((a + (kk % s) * m) % s).astype(np.int32)
    F1 += c1[idx].astype(np.float32); F2 += c2[idx].astype(np.float32)
    cov_th += (c1 * c2).mean() - c1.mean() * c2.mean(); v1 += c1.var(); v2 += c2.var()
print('simulated in %.0f s; theory: covariance %.3f, corr %.5f' % (time.time() - t0, cov_th, cov_th / math.sqrt(v1 * v2)))
corr = float(np.corrcoef(F1, F2)[0, 1]); print('correlation of F1 and F2 over the window: %.5f (se %.5f)' % (corr, 1 / math.sqrt(K)))
for frac in (0.01, 0.001, 0.0001):
    thr = np.quantile(F1, 1 - frac); sel = F1 >= thr; z1 = (F1[sel].mean() - F1.mean()) / F1.std()
    print('top %.2f%% of F1 (+%.2f sd): mean F2 %.3f against overall %.3f (sd %.3f): shift %+.3f sd of F2 (corr * z1 predicts %+.3f)' % (100 * frac, z1, F2[sel].mean(), F2.mean(), F2.std(), (F2[sel].mean() - F2.mean()) / F2.std(), corr * z1))

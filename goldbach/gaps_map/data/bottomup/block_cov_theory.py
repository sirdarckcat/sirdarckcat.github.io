# Exact covariance of the strike counts of the two row blocks over the residue of N modulo each sieve prime (no simulation): Cov = sum_s [ (1/s) sum_x c1_s(x) c2_s(x) - n1 n2 / s^2 ].
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]; cls = np.load('../lattice/cls_sa_11.npy'); alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; R1 = R[R < 170000]; R2 = R[R >= 170000]
for zmax in (4000, 100000, 2000000):
    cov = v1 = v2 = 0.0
    for s in primes_upto(zmax):
        s = int(s)
        if s <= 463: continue
        if s < 2000:
            c1 = np.bincount(R1 % s, minlength=s).astype(np.float64); c2 = np.bincount(R2 % s, minlength=s).astype(np.float64)
            cov += (c1 * c2).mean() - c1.mean() * c2.mean(); v1 += c1.var(); v2 += c2.var()
        else:                      # sparse regime: classes hold at most a few rows; use the exact pair count
            r1 = R1 % s; r2 = R2 % s; both = len(np.intersect1d(r1, r2)) if False else 0
            u1, k1 = np.unique(r1, return_counts=True); u2, k2 = np.unique(r2, return_counts=True)
            common, i1, i2 = np.intersect1d(u1, u2, return_indices=True); pairs = float((k1[i1] * k2[i2]).sum())
            cov += pairs / s - len(R1) * len(R2) / s ** 2
            m1 = len(R1) / s; m2 = len(R2) / s; v1 += (np.sum(k1.astype(float) ** 2) / s - m1 ** 2); v2 += (np.sum(k2.astype(float) ** 2) / s - m2 ** 2)
    print('primes in (463, %d]: Cov(F1, F2) = %+.4f, Var F1 = %.1f, Var F2 = %.1f, correlation = %+.6f' % (zmax, cov, v1, v2, cov / math.sqrt(v1 * v2)))

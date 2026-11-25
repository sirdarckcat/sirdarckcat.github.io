# A3: is the set of good members additively structured beyond shared pins?  Simulated window of 2e7 members (the real arithmetic: N(k) = c + M k, so N(k+d) = N(k) + M d mod s,
# strikes shared exactly when s | d), strike count F(k) = number of alive rows struck by the primes in (463, 4000]. Top set T = the best fraction of the window.
# Autocorrelation A(d) = #{k : k, k+d in T} by FFT, against (i) independent placement, (ii) the Gaussian shared-variance prediction rho(d) = sum_{s | d} var_s / var_total.
import numpy as np, math, sys, time
from scipy import fft as sfft
from scipy.stats import norm, multivariate_normal
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]; cls = np.load('cls_sa_11.npy' if len(sys.argv) < 4 else sys.argv[3]); alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; n = len(R); K = 20_000_000; zmax = 4000
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7); ss = [int(s) for s in primes_upto(zmax) if s > 463]
F = np.zeros(K, dtype=np.float32); kk = np.arange(K, dtype=np.int64); var_s = {}; t0 = time.time()
for s in ss:
    c = np.bincount(R % s, minlength=s).astype(np.float32); a = int(rng.integers(s)); m = int(rng.integers(1, s))
    F += c[((a + (kk % s) * m) % s).astype(np.int32)]; var_s[s] = float(c.var())
mu, sd = float(F.mean()), float(F.std()); vtot = sum(var_s.values()); print('rows %d, window %.0e, primes %d, mean strikes %.1f sd %.1f (model sd %.1f) in %.0f s' % (n, K, len(ss), mu, sd, math.sqrt(vtot), time.time() - t0), flush=True)
np.save('/tmp/F_window.npy', F)
frac = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
thr = np.quantile(F, 1 - frac); T = (F >= thr).astype(np.float64); nT = int(T.sum()); z = (thr - mu) / sd
print('top fraction %.4f: %d members, threshold mean + %.2f sd' % (frac, nT, z), flush=True)
L = 1 << 26; ft = sfft.rfft(T, L); A = sfft.irfft(ft * np.conj(ft), L)[:K]; A = np.rint(A)           # A[d] = #{k: k, k+d in T}
d = np.arange(K); E = (K - d) * (nT / K) ** 2
D = 2_000_000
# Gaussian prediction of the pair excess factor for correlation rho at level z
def pair_excess(rho, z):
    if rho <= 0: return 1.0
    p2 = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]]).cdf([-z, -z]) if False else None
    # P(Z1 > z, Z2 > z) by 1-d integral: int phi(x) P(Z2 > z | Z1 = x) dx
    x = np.linspace(z, 9, 4000); dx = x[1] - x[0]; cond = norm.sf((z - rho * x) / math.sqrt(1 - rho ** 2)); return float((norm.pdf(x) * cond).sum() * dx / norm.sf(z) ** 2)
ratio = np.ones(D + 1); ratio[1:] = A[1:D + 1] / E[1:D + 1]
# band primes dividing each d <= D
nb = np.zeros(D + 1, dtype=np.int8); rho_d = np.zeros(D + 1)
for s in ss:
    nb[s::s] += 1; rho_d[s::s] += var_s[s] / vtot
print('mean ratio over all d <= %d: %.4f (should be 1 up to the finite-set correction)' % (D, ratio[1:].mean()))
for lab, sel in (('d with no band prime factor', nb == 0), ('d divisible by exactly one band prime', nb == 1), ('d divisible by exactly two band primes', nb == 2)):
    sel = sel.copy(); sel[0] = False
    if sel.sum() == 0: continue
    pred = np.mean([pair_excess(r, z) for r in rho_d[sel][::max(1, sel.sum() // 400)]])
    print('%-42s: %8d lags, measured pair ratio %.3f +- %.3f, Gaussian shared-variance prediction %.3f' % (lab, sel.sum(), ratio[sel].mean(), ratio[sel].std() / math.sqrt(sel.sum()), pred))
print('by the band prime s (single-prime multiples only):')
for lo, hi in ((463, 600), (600, 900), (900, 1500), (1500, 2500), (2500, 4000)):
    rs, ps = [], []
    for s in ss:
        if lo <= s < hi:
            idx = np.arange(s, D + 1, s); idx = idx[nb[idx] == 1]
            if len(idx): rs.append(ratio[idx].mean()); ps.append(pair_excess(var_s[s] / vtot, z))
    print('   s in [%4d, %4d): measured %.3f, predicted %.3f (%d primes)' % (lo, hi, np.mean(rs), np.mean(ps), len(rs)))
# energy: sum A(d)^2 against the independent value (over d <= D)
print('additive energy proxy sum_d A(d)^2 over 1 <= d <= %d: measured / independent = %.4f' % (D, (A[1:D + 1] ** 2).sum() / (E[1:D + 1] ** 2 + E[1:D + 1]).sum()))

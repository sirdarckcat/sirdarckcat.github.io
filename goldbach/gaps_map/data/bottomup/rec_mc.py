# Calibration of the success model against the published records of the least Goldbach summand (N up to 9e17), without Gaussian approximations:
# k = number of odd primes p < P with N - p coprime to all odd primes r <= R, sampled over uniform random classes (Monte Carlo, S covers); a cover with k alive rows succeeds
# with probability (1 - pi)^k, pi = 2 prod_{3<=r<=R} r/(r-1)/ln N (every alive row is prime with chance pi, independently).
#  (a) for each record holder: the weighted CDF u of its own k under the tilted measure w = (1-pi)^k (uniform on (0,1) under the model);
#  (b) Lambda(N, F(N)+) = expected number of N' <= N with g(N') > F(N), F(N) = the record level reached at N: exp(-Lambda) is uniform on (0,1) under the model (Lambda ~ Exp(1)).
import numpy as np, math, sys, time
rng = np.random.default_rng(11)
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
recs = [tuple(map(int, l.split())) for l in open('records.txt')]
def choose_R(N):
    R = 3; prod = 3
    for r in primes_upto(300):
        if r <= 3: continue
        if prod * int(r) <= N / 30: prod *= int(r); R = int(r)
        else: break
    return R
def kdist(P, R, S):
    rows = primes_upto(P - 1); rows = rows[rows > 2].astype(np.int64); n = len(rows); rs = [int(r) for r in primes_upto(R) if r > 2]; rowmod = [(rows % r).astype(np.int16) for r in rs]
    ks = np.empty(S, np.int32); chunk = 20000
    for s0 in range(0, S, chunk):
        m = min(chunk, S - s0); alive = np.ones((m, n), bool)
        for r, rm in zip(rs, rowmod):
            c = rng.integers(0, r, size=m).astype(np.int16); alive &= (rm[None, :] != c[:, None])
        ks[s0:s0 + m] = alive.sum(1)
    return ks, n, rs, rows
def pi_of(N, R):
    rs = [int(r) for r in primes_upto(R) if r > 2]; return 2 * np.prod([r / (r - 1) for r in rs]) / math.log(N)
S = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
print('(a) record holders: weighted CDF of the observed alive-row count under the tilted measure')
print('  k            N     p_k  R  rows  mean k  pi    k_obs  tilted mean  tilted 5%-95%   ESS    u')
us = []
for k, N, p in recs:
    if N < 1e9 or p < 1000 or p == 0: continue
    R = choose_R(N); t0 = time.time(); ks, n, rs, rows = kdist(p, R, S); pi = pi_of(N / 1.5, R); w = (1 - pi) ** ks.astype(float)
    ok = np.ones(n, bool)
    for r in rs: ok &= ((N - rows) % r != 0)
    ko = int(ok.sum()); sw = w.sum(); u = (w[ks < ko].sum() + 0.5 * w[ks == ko].sum()) / sw; ess = sw ** 2 / (w ** 2).sum()
    order = np.argsort(ks); cw = np.cumsum(w[order]) / sw; q05, q95 = ks[order][np.searchsorted(cw, 0.05)], ks[order][np.searchsorted(cw, 0.95)]
    us.append(u); print('%3d %16d %6d %2d %5d %7.1f %.3f %6d %9.1f   %4d-%4d %8.0f %.3f' % (k, N, p, R, n, ks.mean(), pi, ko, (w * ks).sum() / sw, q05, q95, ess, u), flush=True)
us = np.array(us); from scipy.stats import kstest
print('u over %d records: mean %.3f (0.5 expected, se %.3f), KS p-value against uniform %.3f' % (len(us), us.mean(), 0.2887 / math.sqrt(len(us)), kstest(us, 'uniform').pvalue))
print('\n(b) Lambda(N, F(N)+) on a grid of N: F(N) = record level reached by N')
print('        N       F(N)  R  rows   Lambda   ln Lambda   exp(-Lambda)')
lam = []
for N in [10 ** e for e in range(8, 18)] + [3 * 10 ** 17, 9 * 10 ** 17, 3 * 10 ** 18]:
    F = max([p for k, Nk, p in recs if Nk <= N and p > 0] + [0])
    if N > 906030579562279642: F = 9341        # the table's last known level (records 68, 69 have no listed p)
    R = choose_R(N); ks, n, rs, rows = kdist(F + 1, R, S)
    L = 0.0                                         # sum over even N' <= N of E_c[(1-pi(N'))^k], in dyadic shells
    for j in range(0, 5):
        Nj = N / 2 ** (j + 0.5); pij = pi_of(Nj, R); L += (N / 2 ** (j + 1)) / 2 * np.mean((1 - pij) ** ks.astype(float))
    lam.append(L); print('%.2e %6d %2d %5d %9.3g %8.2f %9.3f' % (N, F, R, n, L, math.log(L), math.exp(-L)), flush=True)
lam = np.array(lam[:-3]); print('over the 10 decades N = 1e8 ... 1e17: mean ln Lambda %.2f (Exp(1): -0.58, sd 1.28 per point), median Lambda %.2f' % (np.log(lam).mean(), np.median(lam)))

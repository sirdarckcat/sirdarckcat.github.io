# Time-rescaling test of the success model against the record table (exact under a Poisson model of hits).
# After record k-1 (N_{k-1}, level p_{k-1}) the next record is the first N > N_{k-1} with g(N) > p_{k-1}.  With intensity lambda(N) = (1/2) E_c[(1-pi)^{k(c)}] per integer N
# (k = alive odd primes <= p_{k-1}), W_k = integral of lambda over (N_{k-1}, N_k) is Exp(1) and independent across k; and the level of the new record has survival function
# S(P) = E[(1-pi)^{k_P}] / E[(1-pi)^{k_{p_{k-1}}}], so U_k = S(p_k) is Uniform(0,1).
import numpy as np, math, sys, time
rng = np.random.default_rng(23)
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
def pi_of(N, R):
    rs = [int(r) for r in primes_upto(R) if r > 2]; return 2 * np.prod([r / (r - 1) for r in rs]) / math.log(N)
S = int(sys.argv[1]) if len(sys.argv) > 1 else 200000; kmin = int(sys.argv[2]) if len(sys.argv) > 2 else 28
print('  k            N     p_{k-1}   p_k  R   pi     E_prev      W_k    U_k   (W ~ Exp(1), U ~ U(0,1))')
Ws, Us, ks_ = [], [], []
for i in range(1, 67):
    k, N, p = recs[i]; kp, Np, pp = recs[i - 1]
    if k < kmin: continue
    R = choose_R(N); rows = primes_upto(p - 1); rows = rows[rows > 2].astype(np.int64); n = len(rows); rs = [int(r) for r in primes_upto(R) if r > 2]
    rowmod = [(rows % r).astype(np.int16) for r in rs]; nprev = int((rows <= pp).sum())
    kprev = np.empty(S, np.int32); knew = np.empty(S, np.int32); chunk = 20000
    for s0 in range(0, S, chunk):
        m = min(chunk, S - s0); alive = np.ones((m, n), bool)
        for r, rm in zip(rs, rowmod):
            c = rng.integers(0, r, size=m).astype(np.int16); alive &= (rm[None, :] != c[:, None])
        kprev[s0:s0 + m] = alive[:, :nprev].sum(1); knew[s0:s0 + m] = alive.sum(1)
    Nbar = math.sqrt(N * Np); pi = pi_of(Nbar, R); q = 1 - pi
    Eprev = np.mean(q ** kprev.astype(float)); Enew = np.mean(q ** knew.astype(float))
    W = (N - Np) / 2 * Eprev; U = Enew / Eprev
    Ws.append(W); Us.append(U); ks_.append(k); print('%3d %17d %7d %6d %2d %.3f %10.3e %8.3f %6.3f' % (k, N, pp, p, R, pi, Eprev, W, U), flush=True)
Ws = np.array(Ws); Us = np.array(Us); from scipy.stats import kstest, expon
print('\nrecords used: %d (k >= %d)' % (len(Ws), kmin))
print('W: mean %.2f (1 expected, se %.2f), median %.2f (0.69), mean ln W %.2f (-0.58 expected, se %.2f), KS p-value against Exp(1): %.3f' % (Ws.mean(), 1 / math.sqrt(len(Ws)), np.median(Ws), np.log(Ws).mean(), 1.28 / math.sqrt(len(Ws)), kstest(Ws, 'expon').pvalue))
print('U: mean %.3f (0.5 expected, se %.3f), KS p-value against uniform: %.3f' % (Us.mean(), 0.2887 / math.sqrt(len(Us)), kstest(Us, 'uniform').pvalue))
half = len(Ws) // 2
print('first half (k = %d..%d): mean ln W %.2f ; second half: mean ln W %.2f ; U means %.3f and %.3f' % (ks_[0], ks_[half - 1], np.log(Ws[:half]).mean(), np.log(Ws[half:]).mean(), Us[:half].mean(), Us[half:].mean()))

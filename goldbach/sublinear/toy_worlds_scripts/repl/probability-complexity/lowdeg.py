#!/usr/bin/env python3
"""lowdeg.py: the low-degree likelihood ratio for the planted version of 'find k < K with extreme sum_p f_p(k mod p)'.
Null Q: every table entry Y_p(c) iid N(0,1).  Planted P: k* uniform in [0,K), Y_p(c) = mu_p [c = k* mod p] + N(0,1).
||L^{<=D}||^2 = E_{k,k'} exp^{<=D}( sum_{p | k-k'} mu_p^2 )   (Hermite expansion; checked below by brute force).
Part 1: brute-force check of the identity in a miniature (enumerating every monomial of degree <= 3).
Part 2: the real window (K = 21,378,978) and the real later primes to 10^8 with mu_p^2 = Lambda v_p, v_p ~ 1/p."""
import math, itertools, numpy as np
from collections import Counter
def expD(x, D): return sum(x ** d / math.factorial(d) for d in range(D + 1))
# ---- part 1
ps = [5, 7, 11, 13]; K = 300; mu2 = {5: 0.9, 7: 0.7, 11: 0.5, 13: 0.4}
var = [(p, c) for p in ps for c in range(p)]
theta = [{(p, k % p): math.sqrt(mu2[p]) for p in ps} for k in range(K)]
for D in (1, 2, 3):
    form = sum(expD(sum(mu2[p] for p in ps if (k - k2) % p == 0), D) for k in range(K) for k2 in range(K)) / K / K
    # brute force: sum over multi-indices alpha, |alpha| <= D, of (E_k theta_k^alpha)^2 / alpha!
    tot = Counter()
    for k in range(K):
        items = list(theta[k].items())           # only 4 nonzero coordinates per k
        for d in range(D + 1):
            for comb in itertools.combinations_with_replacement(range(4), d):
                cnt = Counter(comb); key = tuple(sorted((items[i][0], e) for i, e in cnt.items()))
                val = math.prod(items[i][1] ** e for i, e in cnt.items()); tot[key] += val / K
    brute = sum(v * v / math.prod(math.factorial(e) for _, e in key) for key, v in tot.items())
    print(f"miniature (primes {ps}, K={K}) D={D}: formula {form:.10f}  brute force over {len(tot)} monomials {brute:.10f}")
# Monte Carlo: the degree-1 optimal statistic f = sum_{p,c} (E theta_{p,c}) Y_{p,c}: advantage^2/Var_Q = ||L^{<=1}||^2 - 1
rng = np.random.default_rng(1); idx = {v: i for i, v in enumerate(var)}; n = len(var)
m1 = np.zeros(n)
for k in range(K):
    for key, val in theta[k].items(): m1[idx[key]] += val / K
T = 200000; Yq = rng.standard_normal((T, n)); ks = rng.integers(0, K, T); Yp = rng.standard_normal((T, n))
for t in range(T):
    for key, val in theta[ks[t]].items(): Yp[t, idx[key]] += val
fq, fp = Yq @ m1, Yp @ m1
print(f"   Monte Carlo, degree 1: (E_P f - E_Q f)^2 / Var_Q f = {(fp.mean()-fq.mean())**2/fq.var():.5f} +- {2*math.sqrt((fp.var()+fq.var())/T)*abs(fp.mean())/fq.var():.5f}; formula ||L^<=1||^2 - 1 = {float(m1@m1):.5f}")
# ---- part 2
K = 21378978; lnK = math.log(K)
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes(100000000); P = P[P > 463]; v = 1.0 / P; v /= v.sum()
print(f"real window: K={K}, ln K={lnK:.3f}; later primes to 1e8: {len(P)}; sum 1/p = {(1.0/P).sum():.4f}; largest v_p = {v[0]:.5f}")
rho = np.zeros(K, dtype=np.float64)
for p, vp in zip(P[P < K].tolist(), v[P < K].tolist()): rho[p::p] += vp
rho[0] = 0; wts = 2.0 * (K - np.arange(K)) / K / K; wts[0] = 0
print(f"   overlap rho(Delta) over all 0<Delta<K: max {rho.max():.5f}, mean {(wts*rho).sum():.3e}")
print("c = Lambda/ln K | planted member's z (= sqrt(Lambda)) vs null maximum sqrt(2 ln K) = %.2f | off-diagonal term (full exp) | diagonal term (1/K)(exp^{<=D}(Lambda)-1) for D = 1..12 | D* = largest D with total <= 1" % math.sqrt(2 * lnK))
for c in (2.0, 2.5, 3.0, 4.0, 6.0):
    Lam = c * lnK; off = float((wts * np.expm1(Lam * rho)).sum())
    diag = [(expD(Lam, D) - 1) / K for D in range(1, 40)]
    Dstar = max([D for D in range(1, 40) if diag[D - 1] + off <= 1] or [0])
    print(f"  {c} | {math.sqrt(Lam):.2f} | {off:.2e} | " + " ".join(f"{x:.1e}" for x in diag[:12]) + f" | D* = {Dstar}  (D*/ln K = {Dstar/lnK:.2f})")

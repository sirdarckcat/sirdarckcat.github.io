import numpy as np, math, sys
from math import lgamma, exp, log, sqrt
import os
ROWS = os.path.dirname(os.path.abspath(__file__)) + '/'
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]
cls = np.load(ROWS + 'cls_sa_11.npy'); alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; n = len(R); lnK = float(sys.argv[1]) if len(sys.argv) > 1 else 16.9; x = 463
print('alive rows of the annealed cover: n =', n, ' window ln K =', lnK)
ZMAX = 60000; ps = primes_upto(ZMAX); ps = ps[ps > x]
# exact residue-count tables of the real rows for every prime in (463, ZMAX]
def tables(s):
    c = np.bincount(R % s, minlength=s).astype(float); return c
E = {}   # per prime: moments of the count c(r) over uniform r: E[min(c,e)] e=1,2,3 ; E[c]; E[c^2]; list size
for s in ps:
    c = tables(int(s)); lns = log(s)
    E[int(s)] = dict(lns=lns, m1=[np.minimum(c, e).mean() for e in (1, 2, 3)], v1=[np.minimum(c, e).var() for e in (1, 2, 3)], mc=c.mean(), mc2=(c ** 2).mean(), vc=c.var(), ell=float((c >= 1).sum()))
def sums(z, e=1):
    ss = [int(s) for s in ps if s <= z]
    lnP = e * sum(E[s]['lns'] for s in ss); mean = sum(E[s]['lns'] * E[s]['m1'][e - 1] for s in ss); sd = sqrt(sum(E[s]['lns'] ** 2 * E[s]['v1'][e - 1] for s in ss))
    ellsum = sum(E[s]['lns'] * E[s]['ell'] for s in ss)
    return ss, lnP, mean, sd, ellsum
print('\n(A) Research\'s table recomputed from the real rows (exact residue counts, not Poisson): (463, z], cap e')
print('   z    e   lnP   typical smooth part, sd | needed sqrt(n lnK lnP) | typical/needed | best-of-window(+5.4sd)/needed')
best = (0, None)
for z in (1000, 1500, 2300, 4000, 10000, 50000):
    for e in (1, 2, 3):
        ss, lnP, mean, sd, ellsum = sums(z, e); need = sqrt(n * lnK * lnP); r = mean / need
        if r > best[0]: best = (r, (z, e))
        print('%6d  %d  %6.0f   %6.0f, %4.0f | %6.0f | %.3f | %.3f' % (z, e, lnP, mean, sd, need, r, (mean + 5.4 * sd) / need))
print('   best typical/needed on this grid: %.3f at (z, e) = %s' % best)
print('\n(B) Variants.  ratio = (agreement of the target) / sqrt(lnK * cost); success of any Coppersmith/GSS-type decoder needs ratio >= 1')
print('   B1 hard lists with their true sizes (GSS: cost = sum_s ln s * |R mod s| instead of n*lnP), e = 1:')
for z in (1500, 2300, 4000, 10000):
    ss, lnP, mean, sd, ellsum = sums(z, 1); print('      z=%6d  typical/needed %.3f  (Coppersmith with degree n: %.3f)  best-of-window %.3f' % (z, mean / sqrt(lnK * ellsum), mean / sqrt(n * lnK * lnP), (mean + 5.4 * sd) / sqrt(lnK * ellsum)))
# B2 soft decoding with weights w(s,r) = alpha_s * c_s[r]  (GSS soft-decision, reliabilities = number of rows in the class)
def soft(z, zq=5.4):
    ss = [int(s) for s in ps if s <= z]
    a = np.array([E[s]['lns'] * E[s]['mc'] for s in ss]); v = np.array([E[s]['lns'] ** 2 * E[s]['vc'] for s in ss]); cst = np.array([E[s]['lns'] * s * E[s]['mc2'] for s in ss])   # cost: ln s * sum_r c_r^2 = ln s * s * E[c^2]
    alpha = a / cst                                                                                                                               # CS-optimal for the typical member
    typ = (alpha * a).sum() / sqrt(lnK * (alpha ** 2 * cst).sum()); best_ = ((alpha * a).sum() + zq * sqrt((alpha ** 2 * v).sum())) / sqrt(lnK * (alpha ** 2 * cst).sum())
    # numerical optimum of the best-member ratio over all alpha >= 0
    from scipy.optimize import minimize
    f = lambda la: -(((np.exp(la) * a).sum() + zq * sqrt((np.exp(2 * la) * v).sum())) / sqrt(lnK * (np.exp(2 * la) * cst).sum()))
    res = minimize(f, np.log(alpha / alpha.max()), method='L-BFGS-B', options=dict(maxiter=400)); return typ, best_, -res.fun
print('   B2 soft decoding, weights = row counts, per-prime scale optimised (GSS soft-decision ceiling):')
for z in (1500, 2300, 4000, 10000, 50000):
    typ, bst, opt = soft(z); print('      z=%6d  typical/needed %.3f  best-of-window %.3f  optimised over all per-prime scales %.3f' % (z, typ, bst, opt))
print('   closed form: ratio^2 <= ln(1 + n/x)/lnK = %.4f -> typical/needed <= %.3f for ANY prime band beyond x = 463' % (math.log(1 + n / x) / lnK, sqrt(math.log(1 + n / x) / lnK)))
print('   B3 subsets of the rows (hard lists, z = 4000, e = 1): n_sub -> typical/needed')
rng = np.random.default_rng(1)
for ns in (100, 300, 700, n):
    Rs = R[rng.permutation(n)[:ns]]; ss = [int(s) for s in ps if s <= 4000]
    mean = sum(log(s) * (np.bincount(Rs % s, minlength=s) >= 1).mean() for s in ss); lnP = sum(log(s) for s in ss)
    print('      n = %4d  typical smooth part %6.0f  needed %6.0f  ratio %.3f  ratio^2 %.4f' % (ns, mean, sqrt(ns * lnK * lnP), mean / sqrt(ns * lnK * lnP), mean ** 2 / (ns * lnK * lnP)))
print('   B4 product of m shifted copies F(k+a_1)...F(k+a_m) (degree n*m; every prime counted once; z = 4000, e = 1):')
ss = [int(s) for s in ps if s <= 4000]; lnP = sum(log(s) for s in ss); pS = np.array([1 - exp(-n / s) for s in ss]); lns = np.array([log(s) for s in ss])
for m in (1, 2, 3, 5, 10, 30, 100, 1000):
    d = (lns * (1 - (1 - pS) ** m)).sum(); print('      m = %4d  agreement %6.0f  needed %7.0f  ratio %.3f' % (m, d, sqrt(n * m * lnK * lnP), d / sqrt(n * m * lnK * lnP)))
print('   B5 necessary condition: agreement <= ln P, so ratio^2 <= lnP/(n lnK): for lnP = 3,468: ratio <= %.3f whatever the member is' % sqrt(3468 / (n * lnK)))
print('   B6 pinning entropy first: window ln K\' = %.1f - (nats pinned) ; typical/needed at z = 4000, e = 1 (agreement %.0f):' % (lnK, sums(4000, 1)[2]))
ss_, lnP4, mean4, sd4, _ = sums(4000, 1)
for pin in (0, 6.3, 12.6, 16.0, 16.5, 16.9):
    lk = max(lnK - pin, 1e-9); print('      pinned %.1f nats -> ln K\' = %.2f : typical/needed %.3f' % (pin, lk, mean4 / sqrt(n * lk * lnP4)))
print('   B7 the window the method could handle for the typical member (hard lists, Coppersmith): ln K <= agreement^2/(n lnP) = %.2f nats; soft ceiling ln(1+n/x) = %.2f nats' % (mean4 ** 2 / (n * lnP4), math.log(1 + n / x)))
print('   B8 cost: Coppersmith lattice has dimension >= n = %d with entries of >= %d bits (z = 4000): LLL ~ dim^4 * bits = %.1e bit-operations at the very least; the sieve over a window of K = e^%.1f members costs about K * 1,500 marks = %.1e' % (n, int(lnP4 / math.log(2)), n ** 4 * (lnP4 / math.log(2)), lnK, math.exp(lnK) * 1500))

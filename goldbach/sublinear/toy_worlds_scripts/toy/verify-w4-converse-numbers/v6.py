import math, random, numpy as np, sympy, gmpy2
from vlib import *
cov, rows = get(); n = len(rows); rng = np.random.default_rng(31337); P = lp(467, 5000)
# (a) character sums by direct evaluation with a discrete-log table from sympy's primitive root
pw = {e: [] for e in (2, 3, 4, 5, 6)}; allmean = []; allmax = []; cos = {e: [] for e in (2, 3, 4, 5, 6, 7, 8, 10, 12)}; cosr = {e: [] for e in cos}
W2 = {}
for s in P:
    g = int(sympy.primitive_root(s)); ind = np.zeros(s, dtype=np.int64); x = 1
    for j in range(s - 1): ind[x] = j; x = x * g % s
    r = rows % s; r = r[r != 0]; mm = len(r); ir = ind[r]
    hist = np.bincount(ir, minlength=s - 1).astype(float)
    # all nontrivial characters: chi_k(q) = exp(2 pi i k ind(q)/(s-1)); power via direct DFT definition (matrix-free): use np.fft only here
    Pk = np.abs(np.fft.fft(hist)) ** 2 / mm; allmean.append(Pk[1:].mean()); allmax.append(Pk[1:].max() / math.log(s - 2))
    for e in pw:
        if (s - 1) % e == 0:
            vals = []
            for tt in range(1, e):
                if math.gcd(tt, e) == 1:
                    sm = np.exp(2j * np.pi * ((ir * tt) % e) / e).sum(); vals.append(abs(sm) ** 2 / mm)     # direct sum, character of exact order e
            pw[e].append(np.mean(vals))
    for e in cos:
        if (s - 1) % e == 0:
            cc = np.bincount(ir % e, minlength=e); cos[e].append((cc.max() / ((s - 1) / e) - mm / (s - 1)) / math.log(e))
            rr = np.bincount(rng.integers(0, s - 1, mm) % e, minlength=e); cosr[e].append((rr.max() / ((s - 1) / e) - mm / (s - 1)) / math.log(e))
print("(a) order: mean power +- se (primes)")
for e in pw: print("   ", e, "%.3f +- %.3f (%d)" % (np.mean(pw[e]), np.std(pw[e]) / math.sqrt(len(pw[e])), len(pw[e])))
print("    all nontrivial: mean %.4f ; max/ln(s-2): mean %.3f max %.3f" % (np.mean(allmean), np.mean(allmax), np.max(allmax)))
print("    heaviest coset rate real(random): " + "; ".join("e=%d %.4f (%.4f) [%d]" % (e, np.mean(cos[e]), np.mean(cosr[e]), len(cos[e])) for e in cos))
# (b) Legendre sums with gmpy2.jacobi
AP = lp(467, Q)
def legsum(s):
    r = rows % s; return int(sum(gmpy2.jacobi(int(x), s) for x in r))
# faster: Euler table
def legtab(s):
    t = np.full(s, -1, dtype=np.int64); t[(np.arange(1, s, dtype=np.int64) ** 2) % s] = 1; t[0] = 0; return t
W = {}
for s in AP: W[s] = int(legtab(s)[rows % s].sum())
assert all(W[s] == legsum(s) for s in AP[:40])
for hi in (5000, 20000, 200000):
    ss = [s for s in AP if s <= hi]; g = sum(abs(W[s]) / (s - 1) for s in ss)
    print("(b) to %d: %d primes, free-sign gain %.2f rows = %.3f nats, constraint %.1f nats, mean|W|/sqrt(n) %.3f" % (hi, len(ss), g, g * 0.0243, len(ss) * math.log(2), np.mean([abs(W[s]) for s in ss]) / math.sqrt(n)))
print("    |W(467)| =", abs(W[467]), "gain", abs(W[467]) / 466)
# signed bias (verifier's addition): mean of W[s] by range, and the all-residue / all-non-residue gain
for lo, hi in ((467, 1000), (1000, 2000), (2000, 5000), (467, 5000), (5000, 20000), (20000, 200000)):
    ww = np.array([W[s] for s in AP if lo <= s < hi]); print("    signed: s in [%d,%d): %d primes, mean W = %+.2f +- %.2f (sd %.1f; noise sd %.1f), sum W/(s-1) = %+.3f" % (lo, hi, len(ww), ww.mean(), ww.std() / math.sqrt(len(ww)), ww.std(), math.sqrt(n), sum(W[s] / (s - 1) for s in AP if lo <= s < hi)))
# all primes < Q : sum of Legendre over ALL odd primes 463<q<Q (Chebyshev-type bias) for comparison
allq = np.array(list(sympy.primerange(467, Q)), dtype=np.int64)
ww = np.array([legtab(s)[allq % s].sum() for s in P]); print("    all %d primes in (463,Q): mean sum of (q/s) over s in 467..5000 = %+.2f +- %.2f ; rows are %.4f of them" % (len(allq), ww.mean(), ww.std() / math.sqrt(len(ww)), n / len(allq)))
# (c) forced signs
Mm = 2 * math.prod(cov); C = np.array([c for c in range(1, 100001) if math.gcd(c, Mm) == 1], dtype=np.int64)
for hi in (5000, 20000):
    acc = np.zeros(len(C))
    for s in AP:
        if s > hi: break
        acc += legtab(s)[C % s] * (W[s] / (s - 1))
    i = int(acc.argmax()); print("(c) to %d: %d c's mean %+.3f sd %.3f pred sd %.3f best %+.3f at c=%d ; c=1: %+.3f ; z-score of c=1: %.1f" % (hi, len(C), acc.mean(), acc.std(), math.sqrt(sum((W[s] / (s - 1)) ** 2 for s in AP if s <= hi)), acc[i], C[i], acc[0], acc[0] / acc.std()))
    # squares c = b^2 all give the same as c=1; how many c have gain < c=1?
    print("     number of c with gain <= gain(1):", int((acc <= acc[0] + 1e-9).sum()), "(perfect squares coprime to M below 1e5:", int(sum(1 for c in C if math.isqrt(int(c)) ** 2 == c)), ")")
# (d) Prop D instances: same targets (RNG order) and generators as the page; own elimination; verify with jacobi
random.seed(2)
for m in (10, 20, 40, 80):
    tg = AP[:m]; gens = AP[m:2 * m + 8]; target = [random.choice((1, -1)) for _ in tg]
    A = np.array([[0 if gmpy2.jacobi(p, s) == 1 else 1 for p in gens] + [0 if t == 1 else 1] for s, t in zip(tg, target)], dtype=np.uint8)
    J = len(gens); r = 0; piv = []
    for col in range(J):
        nzr = np.nonzero(A[r:, col])[0]
        if len(nzr) == 0: continue
        p0 = r + nzr[0]; A[[r, p0]] = A[[p0, r]]
        for i in range(m):
            if i != r and A[i, col]: A[i] ^= A[r]
        piv.append(col); r += 1
        if r == m: break
    assert r == m
    x = np.zeros(J, dtype=int); x[piv] = A[:m, J]
    c = math.prod(p for p, b in zip(gens, x) if b)
    ok = all(gmpy2.jacobi(c, s) == t for s, t in zip(tg, target))
    print("(d) m=%d targets at %d..%d, c = product of %d primes of %d..%d, ln c %.1f, m ln2 %.1f, verified %s, free gain %.3f rows, ln c per sign %.2f" % (m, tg[0], tg[-1], x.sum(), gens[0], gens[-1], math.log(c), m * math.log(2), ok, sum(abs(W[s]) / (s - 1) for s in tg), math.log(c) / m))

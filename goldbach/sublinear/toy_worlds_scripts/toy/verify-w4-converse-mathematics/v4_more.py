#!/usr/bin/env python3
import math, random, numpy as np, sympy, flint, itertools, time
from fractions import Fraction
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
line = [x for x in open(COVER) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows = np.array([q for q in sympy.primerange(3, Q) if all(q % r != a for r, a in cov)]); n = len(rows)
# A. Prop E decomposition with standard errors, split by s = s' mod 6
ind = np.zeros(Q); ind[rows] = 1
for lo, hi, cnt in ((467, 1000, 78), (1000, 2000, 135)):
    pr = list(sympy.primerange(lo, hi)); tabs = {s: np.bincount(rows % s, minlength=s).astype(float) for s in pr}
    rec = {True: [], False: []}
    for i, s in enumerate(pr):
        one = ind[:s]; g = tabs[s] - one
        for s2 in pr[i + 1:]:
            f2 = tabs[s2][:s]; g2 = f2 - one; cv = lambda x, y: np.mean(x * y) - x.mean() * y.mean()
            rec[(s - s2) % 6 == 0].append((cv(one, one), cv(one, g2) + cv(g, one), cv(g, g2)))
    for same in (True, False):
        a = np.array(rec[same]); se = a.std(axis=0) / math.sqrt(len(a))
        print(f"[{lo},{hi}) s{'=' if same else '!='}s' mod 6: pairs {len(a)}: Var(1_R) {a[:,0].mean():.3e}; cross terms {a[:,1].mean():+.3e} +- {se[1]:.1e}; Cov(g,g') {a[:,2].mean():+.3e} +- {se[2]:.1e}")
# B. generalised progressions of rank 2: bound (i) with representation counting, arbitrary basis
random.seed(7); viol = 0; tests = 0
for it in range(400):
    m = random.choice((1, 2)); sl = [int(sympy.randprime(5, 40)) for _ in range(m)]
    gens = [[(random.randrange(1, s), random.randrange(1, max(2, s // 2))) for _ in range(2)] for s in sl]; aa = [random.randrange(s) for s in sl]
    K = random.randrange(20, 300); nn = 1 + 2 * m
    # lattice {(k, t_ig)} : k - sum_g d_ig t_ig = 0 mod s_i   (coset shift by a_i handled by counting directly)
    # basis: rows of the kernel lattice via HNF of the congruence system
    # build generating set: e_k' = (P,0..), and for each (i,g): unit t_ig with k adjusted by CRT
    P = math.prod(set(sl))
    if len(set(sl)) < m: continue
    def crt_k(vec):  # k with k = vec[i] mod s_i
        k = 0
        for s, v in zip(sl, vec): k += v * (P // s) * pow(P // s, -1, s)
        return k % P
    G = [[P] + [0] * (2 * m)]
    for i in range(m):
        for g in range(2):
            v = [0] * m; v[i] = gens[i][g][0]; row = [crt_k(v)] + [0] * (2 * m); row[1 + 2 * i + g] = 1; G.append(row)
    A = flint.fmpz_mat(G).lll(); B = [[int(A[i, j]) for j in range(nn)] for i in range(nn)]
    assert abs(int(flint.fmpz_mat(B).det())) == P
    ell = [K] + [gens[i][g][1] for i in range(m) for g in range(2)]
    tau = [Fraction(sum(abs(B[i][j]) for i in range(nn)), ell[j]) for j in range(nn)]
    E = Fraction(K * math.prod(ell[1:]), P)
    cntrep = 0
    for k in range(K):
        r = 1
        for i, s in enumerate(sl):
            r *= sum(1 for t0 in range(gens[i][0][1]) for t1 in range(gens[i][1][1]) if (aa[i] + gens[i][0][0] * t0 + gens[i][1][0] * t1 - k) % s == 0)
        cntrep += r
    lowb = E * math.prod(max(Fraction(0), 1 - t) for t in tau); upb = E * math.prod(1 + t for t in tau); tests += 1
    if not (lowb <= cntrep <= upb): viol += 1
print("rank-2 generalised progressions, bound (i) with representations counted:", tests, "tests,", viol, "violations")
# C. Prop D with e = 3 (small check) 
random.seed(3)
S3 = [s for s in sympy.primerange(467, 700) if s % 3 == 1][:8]; gensp = [p for p in sympy.primerange(700, 900)][:14]
def ind3(x, s):
    g = sympy.primitive_root(s); return int(sympy.discrete_log(s, x % s, g)) % 3
tgt = [random.randrange(3) for _ in S3]
Mx = [[ind3(p, s) for p in gensp] + [t] for s, t in zip(S3, tgt)]
J = len(gensp); r = 0; piv = []
for col in range(J):
    pr_ = next((i for i in range(r, len(S3)) if Mx[i][col] % 3), None)
    if pr_ is None: continue
    Mx[r], Mx[pr_] = Mx[pr_], Mx[r]; inv = pow(Mx[r][col], -1, 3); Mx[r] = [(x * inv) % 3 for x in Mx[r]]
    for i in range(len(S3)):
        if i != r and Mx[i][col] % 3: f = Mx[i][col]; Mx[i] = [(x - f * y) % 3 for x, y in zip(Mx[i], Mx[r])]
    piv.append(col); r += 1
    if r == len(S3): break
x = [0] * J
for i, col in enumerate(piv): x[col] = Mx[i][J]
c = math.prod(p ** e for p, e in zip(gensp, x))
ok = all(ind3(c * pow(random.randrange(2, 10**6), 3), s) == t for s, t in zip(S3, tgt))
print("Prop D, e = 3, 8 prescribed cubic classes: rank", r, "verified for c*y^3:", ok, " ln c =", round(math.log(c), 1))
# cover compatibility of N = c y^2: number of cover primes where a_r is a QR; c<=1e5 coprime to M with (c/r)=(a_r/r) for all r
qr = sum(1 for r_, a in cov if pow(a, (r_ - 1) // 2, r_) == 1); print("a_r quadratic residue at", qr, "of 89 cover primes (N = y^2 itself is in the cover only if 89 of 89)")
Mm = 2 * math.prod(r_ for r_, a in cov); comp = 0
for c in range(1, 100001):
    if math.gcd(c, Mm) != 1: continue
    if all(pow(c, (r_ - 1) // 2, r_) == pow(a, (r_ - 1) // 2, r_) for r_, a in cov): comp += 1
print("c <= 10^5 coprime to M for which c*y^2 can meet the 89 cover classes:", comp, "of 9503")
print("room: sum ln(r/2) over cover primes =", round(sum(math.log(r_ / 2) for r_, a in cov), 1), "nats needed on y; room of y at 200 digits with c=1:", round(200 * math.log(10) / 2, 1))

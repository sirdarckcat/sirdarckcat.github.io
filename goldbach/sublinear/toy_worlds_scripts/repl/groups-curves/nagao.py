"""Weakest point of the root-number substitute, tested.  w(E_n) = -(-1)^omega(n) for E_n: y^2+xy = x^3-36nx-n.
The coefficients a_p(E_n) for small p depend only on n mod p, so they cost nothing.  Does the partial Euler product
(Mestre-Nagao sum S_T(n) = sum_{5<=p<=T} a_p(E_n) ln p / p) know the sign?
1. miniature: n in [10^7, 10^7+600000), gcd(n,6)=1: correlation of S_T with lambda-like sign (-1)^omega(n).
2. real rows: the 50,636 sieved 200-digit rows; primes all have sign +1, composites are mixed: compare the mean of S_T.
If the Euler product at small primes saw the sign, 1. would give a correlation far from 0 and 2. a large z."""
import math, pickle, time, numpy as np, sympy, gmpy2
from common import setup
T = 1000
ps = [p for p in sympy.primerange(5, T)]
tabs = {}
for p in ps:
    leg = np.full(p, -1, dtype=np.int64); leg[(np.arange(p, dtype=np.int64) ** 2) % p] = 1; leg[0] = 0
    x = np.arange(p, dtype=np.int64)[None, :]; t = np.arange(p, dtype=np.int64)[:, None]
    f = (4 * x ** 3 + x ** 2 - 144 * t * x - 4 * t) % p
    tabs[p] = -leg[f].sum(axis=1)                    # a_p(E_t), t mod p
# check one against a direct count
p = 101; t = 17; cnt = sum(1 for x in range(p) for y in range(p) if (y * y + x * y - x ** 3 + 36 * t * x + t) % p == 0) + 1
assert p + 1 - cnt == tabs[p][t]
lo = 10 ** 7; W = 600000
om = np.zeros(W, dtype=np.int64)
for p in sympy.primerange(2, int((lo + W) ** .5) + 1):
    om[(-lo) % p::p] += 1
rem = np.arange(lo, lo + W, dtype=np.int64)
for p in sympy.primerange(2, int((lo + W) ** .5) + 1):
    idx = np.arange((-lo) % p, W, p)
    while len(idx):
        rem[idx] //= p; idx = idx[rem[idx] % p == 0]
om += (rem > 1)
ns = np.arange(lo, lo + W, dtype=np.int64); ok = (ns % 2 != 0) & (ns % 3 != 0)
sign = (-1.0) ** om
for TT in (100, 300, 1000):
    S = np.zeros(W)
    for p in ps:
        if p > TT: break
        S += tabs[p][ns % p] * math.log(p) / p
    c = np.corrcoef(S[ok], sign[ok])[0, 1]
    print(f"miniature, T = {TT}: {ok.sum()} n; corr(S_T, (-1)^omega(n)) = {c:+.4f} +- {1/math.sqrt(ok.sum()):.4f};  sd of S_T {S[ok].std():.2f}")
    # prime n against n with exactly two prime factors
    pr = ok & (om == 1) & (rem == ns) ; two = ok & (om == 2)
rows, cov, N0, M, K = setup()
Sv = pickle.load(open("survivors.pkl", "rb"))
val = []; lab = []
for k, q, b in Sv:
    n = N0 + k * M - q
    val.append(sum(tabs[p][int(n % p)] * math.log(p) / p for p in ps)); lab.append(b)
val = np.array(val); lab = np.array(lab)
m1 = val[lab].mean(); m0 = val[~lab].mean(); se = math.sqrt(val[lab].var() / lab.sum() + val[~lab].var() / (~lab).sum())
print(f"real 200-digit rows, T = {T}: mean S_T primes {m1:+.4f}, composites {m0:+.4f}, difference {m1-m0:+.4f} +- {se:.4f} (z = {(m1-m0)/se:+.2f}); sd of S_T {val.std():.2f}")
# time of one trial division of a 200-digit number by a 30-bit prime, against one Fermat test
n = N0 + 12345 * M - rows[0]; P = [int(p) for p in sympy.primerange(10 ** 8, 10 ** 8 + 200000)]
t = time.perf_counter(); s = sum(1 for p in P if n % p == 0); dt = (time.perf_counter() - t) / len(P)
t = time.perf_counter(); [gmpy2.powmod(2, n - 1, n) for _ in range(300)]; tF = (time.perf_counter() - t) / 300
print(f"N mod p (p near 10^8): {dt*1e9:.0f} ns = {dt/tF:.5f} Fermat tests (python loop included); kills per Fermat-unit for one row by trial division just above 10^8: {1e-8/(dt/tF):.2e}")

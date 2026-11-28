# Mechanism "powers / Carlitz / cyclotomic" in F_q[x] (the analogue of 2^n + c).
# (1) N = x^m:  m = m0 mod (q^D - 1)  <=>  N = x^m0 mod (x^(q^D - 1) - 1), and x^(q^D - 1) - 1 is the product of all monic
#     irreducibles of degree dividing D except x: one congruence of degree q^D - 1 = the total degree of the primes it pins.
# (2) Carlitz module C_T(z) = T z + z^q (T = x):  M = M0 mod Lam  =>  C_M(a) = C_M0(a) mod C_Lam(a), deg C_Lam(a) = q^deg(Lam) deg a.
# (3) rows (monic irreducible, degree <= D) not struck by the primes of degree <= J (pi | N - Q), for N = x^m, for
#     N = C_M(x) and for random N prime to every such prime.
#   python3 powers_ff.py p J D
import itertools, random, sys
import numpy as np
from flint import fq_default_ctx, fq_default_poly_ctx
p, J, D = (int(v) for v in sys.argv[1:4]); q = p; random.seed(3)
F = fq_default_ctx(p, 1); R = fq_default_poly_ctx(F); x = R.gen()
def irr(d): return [R(list(c) + [1]) for c in itertools.product(range(p), repeat=d) if R(list(c) + [1]).is_irreducible()]
primes = [P for j in range(1, J + 1) for P in irr(j)]; rows = [Q for d in range(1, D + 1) for Q in irr(d)]
# (1)
for Dd in (1, 2, 3):
    Lm = q ** Dd - 1; Phi = x ** Lm - 1
    prod = R(1)
    for j in range(1, Dd + 1):
        if Dd % j == 0:
            for P in irr(j):
                if P != x: prod *= P
    assert prod == Phi
    for m in random.sample(range(Lm, 50 * Lm), 20): assert (x ** m - x ** (m % Lm)) % Phi == 0
print(f"(1) F_{q}: x^(q^D-1) - 1 = product of the monic irreducibles of degree | D other than x, and x^m = x^(m mod (q^D-1)) modulo it: checked for D = 1, 2, 3")
# (2) Carlitz
def carlitz(M, a):                      # C_M(a), M in F_q[x]
    co = M.coeffs(); out = R(0); cur = a
    for i, c in enumerate(co):
        out += c * cur; cur = x * cur + cur ** q
    return out
ok = 0
for _ in range(30):
    Lam = R([random.randrange(p) for _ in range(2)] + [1]); M0 = R([random.randrange(p) for _ in range(2)])
    K = R([random.randrange(p) for _ in range(2)] + [1]); M = M0 + K * Lam; a = x + random.randrange(p)
    CL = carlitz(Lam, a); assert CL.degree() == q ** 2
    assert (carlitz(M, a) - carlitz(M0, a)) % CL == 0; ok += 1
print(f"(2) Carlitz: C_M(a) = C_M0(a) mod C_Lam(a) for M = M0 mod Lam, deg C_Lam(a) = q^deg(Lam): {ok} random cases")
# (3)
def key(f): return tuple(int(str(c)) for c in f.coeffs())
def left(N):
    res = {i: N % P for i, P in enumerate(primes)}
    return sum(1 for Q in rows if all((Q - res[i]) % P != 0 or Q == P for i, P in enumerate(primes)) and True)
def left2(N):                            # rows Q with no prime of degree <= J dividing N - Q
    c = 0
    for Q in rows:
        f = N - Q
        if all(f % P != 0 for P in primes): c += 1
    return c
V = R(1)
for P in primes: V *= P
pw = [left2(x ** m) for m in range(60, 260)]
rn = []
while len(rn) < 200:
    N = R([random.randrange(p) for _ in range(150)] + [1])
    if N.gcd(V).degree() == 0: rn.append(left2(N))
rz = []
Vx = V // x
while len(rz) < 200:
    N = x * R([random.randrange(p) for _ in range(149)] + [1])
    if N.gcd(Vx).degree() == 0: rz.append(left2(N))
cm = []
for co in itertools.product(range(p), repeat=4):
    M = R(list(co) + [1]); N = carlitz(M, R(1))          # C_M(1), degree q^3... (deg M = 4 -> q^4 too big for p=3? 81: fine)
    if N.gcd(V).degree() == 0: cm.append(left2(N))
print(f"(3) F_{q}: {len(rows)} rows of degree <= {D}, {len(primes)} primes of degree <= {J}; rows not struck:")
print(f"    N = x^m, m = 60..259 (x^m = 0 mod x, nonzero elsewhere): mean {np.mean(pw):.1f}, sd {np.std(pw):.1f}, min {min(pw)}")
print(f"    random N prime to all the primes (200): mean {np.mean(rn):.1f}, sd {np.std(rn):.1f}, min {min(rn)}")
print(f"    random N = 0 mod x, prime to the other primes (200): mean {np.mean(rz):.1f}, sd {np.std(rz):.1f}, min {min(rz)}")
if cm: print(f"    N = C_M(1), M monic of degree 4, prime to all the primes ({len(cm)}): mean {np.mean(cm):.1f}, sd {np.std(cm):.1f}, min {min(cm)}")

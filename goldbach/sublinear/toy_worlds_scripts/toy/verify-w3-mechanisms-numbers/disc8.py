# congruences modulo 8 for disc(lam~ A~^4 - Q~) over Z (q = 2), verifier's own code
import random, sys
from flint import fmpz_poly, nmod_poly
rng = random.Random(2024)
def rpoly(d, monic=True, lo=-9, hi=9):
    c = [rng.randint(lo, hi) for _ in range(d)] + [1 if monic else rng.choice([-3,-1,1,3,5])]
    return fmpz_poly(c)
def S_mod2(Q):
    c = [int(t) % 2 for t in Q.derivative().coeffs()]
    return nmod_poly([c[i] for i in range(0, len(c), 2)], 2)
cnt = {'odd':0, '0mod4':0, '2mod4':0}; bad = {'odd':0, '0mod4':0, '2mod4':0}
tries = 0
while sum(cnt.values()) < 3000 and tries < 200000:
    tries += 1
    d = rng.randint(1, 10)
    Q = rpoly(d)
    Q2 = nmod_poly([int(t) % 2 for t in Q.coeffs()], 2)
    if Q2.gcd(Q2.derivative()).degree() != 0: continue
    S = S_mod2(Q)
    if S.is_zero(): continue
    a = max(S.degree(), d//4 + 1, 1) + rng.randint(0, 4)
    n = 4*a
    qc = [int(t) for t in Q.coeffs()]
    if d % 2 == 0 and (qc[d-1] % 2 == 0 or n - d < 4): continue
    # A~ : any integer lift of S*B mod 2, monic
    B2 = nmod_poly([rng.randint(0,1) for _ in range(a - S.degree())] + [1], 2)
    A2 = S*B2
    A = fmpz_poly([int(t) + 2*rng.randint(-4, 4) for t in A2.coeffs()[:-1]] + [1])
    lam = rng.choice([-5,-3,-1,1,3,5,7])
    Fp = lam*A**4 - Q
    dF = int(Fp.discriminant()); dQ = int(Q.discriminant())
    if d % 2 == 1:
        ds = d if (d-1)//2 % 2 == 0 else -d
        rhs = (1+4*a)*ds*dQ; key = 'odd'
    elif d % 4 == 0:
        rhs = (1+4*a)*(1+d)*dQ; key = '0mod4'
    else:
        rhs = (1+4*a)*(d-1)*(1+4*qc[d-2])*dQ; key = '2mod4'
    cnt[key] += 1
    if (dF - rhs) % 8: bad[key] += 1
print("cases", cnt, "disagreements", bad)

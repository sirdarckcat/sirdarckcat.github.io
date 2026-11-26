# independent check of Theorem 1 (char 2) by factorisation
import random, sys, itertools
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
k = int(sys.argv[1]); trials = int(sys.argv[2]); q = 2**k
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]
one, zero = F(1), F(0)
def tr(v):
    s = zero; w = v
    for _ in range(k):
        s += w; w = w*w
    assert s == zero or s == one
    return 0 if s == zero else 1
def sqrtF(c):  # c^(q/2)
    return c ** (q//2)
def nfac(f):
    return sum(m for _, m in f.factor()[1])
def Sof(Q):
    co = Q.coeffs(); d = len(co)-1
    # Q' = sum_{i odd} q_i x^(i-1) ; S = sum_{i odd} sqrt(q_i) x^((i-1)/2)
    return R([sqrtF(co[i]) for i in range(1, d+1, 2)])
random.seed(12345 + k)
st = Counter()
def rnd_poly(deg, monic=True):
    return R([random.choice(els) for _ in range(deg)] + [one])
for t in range(trials):
    d = random.randint(1, 11)
    Q = rnd_poly(d)
    mode = random.random()
    if d % 2 == 0 and mode < 0.25:
        co = Q.coeffs(); co[d-1] = zero; Q = R(co)
    if Q.gcd(Q.derivative()).degree() != 0: continue
    S = Sof(Q)
    assert S*S == Q.derivative()
    if S == 0: continue
    divides = random.random() < 0.8
    b = random.randint(0, 3)
    B = rnd_poly(b)
    if divides:
        A = S * B
        A = A * (1/A.coeffs()[-1])
    else:
        A = rnd_poly(S.degree() + b)
        if S.degree() == 0 or A % S == 0: continue
    a = A.degree()
    if a < 1: continue
    lam = random.choice(els[1:])
    N = lam * A**4; n = 4*a
    if d >= n: continue
    f = N - Q
    sqf = f.gcd(f.derivative()).degree() == 0
    r = nfac(f); rQ = nfac(Q); co = Q.coeffs()
    if d % 2 == 1:
        pred = (rQ + 1 + k*(a + (d*d-1)//8)) % 2; cat = 'b'
        if n - d == 1: cat = 'b(n-d=1)'
        if n - d == 3: cat = 'b(n-d=3)'
    else:
        if co[d-1] == zero:
            cat = 'even,q_{d-1}=0,d%%4=%d' % (d % 4)
            # try naive candidate: same as d=0 mod 4 formula
            pred = (rQ + k*(a + d//4)) % 2
        else:
            if d % 4 == 0: pred = (rQ + k*(a + d//4)) % 2; cat = 'c0'
            else: pred = (rQ + k*(a + (d-2)//4) + tr(co[d-2]/co[d-1]**2)) % 2; cat = 'c2'
            if n - d < 4: cat += '(n-d=2)'
    if not divides: cat = 'S∤A:' + cat
    st[(cat, 'ok' if pred == r % 2 else 'BAD')] += 1
    if divides and not sqf: st[(cat, 'NOT SQUAREFREE')] += 1
for key in sorted(st): print(q, key, st[key])

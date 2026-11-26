import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(4)
for k in (1,2,3):
    q = 2**k
    F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; zero=F(0); one=F(1)
    def tr(v):
        s = zero; w = v
        for _ in range(k): s += w; w = w*w
        return 0 if s == zero else 1
    def nfac(f): return sum(m for _, m in f.factor()[1])
    st = Counter()
    for t in range(3000):
        Q = R([random.choice(els), random.choice(els[1:]), random.choice(els), zero, one])
        if Q.gcd(Q.derivative()).degree() != 0: continue
        a = random.randint(3, 6)
        A = R([random.choice(els) for _ in range(a)] + [one]); lam = random.choice(els[1:])
        a1 = A.coeffs()[a-1]
        r = nfac(lam*A**4 - Q); rQ = nfac(Q)
        st[('a1=0' if a1 == zero else 'a1!=0', (r - rQ - 1 - k*a) % 2)] += 1
        # candidate with trace term
        st[('cand Tr(lam a1^4 ... )', (r - rQ - 1 - k*a - tr(a1*a1*a1*a1*lam/ (Q.coeffs()[1])) ) % 2)] += 0
    print("F_%d d=4 q3=0:" % q, sorted(st.items()))

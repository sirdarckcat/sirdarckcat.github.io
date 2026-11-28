import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(5)
for k in (1,2,3):
    q = 2**k
    F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; zero=F(0); one=F(1)
    def nfac(f): return sum(m for _, m in f.factor()[1])
    L1 = x**q + x
    for mult, name in ((L1, 'L1|A'), (L1*L1, 'L1^2|A'), (x*x, 'x^2|A'), (x**2+x+one, '(x^2+x+1)|A')):
        st = Counter()
        for t in range(1200):
            Q = R([random.choice(els), random.choice(els[1:]), random.choice(els), zero, one])
            if Q.gcd(Q.derivative()).degree() != 0: continue
            b = random.randint(1, 4)
            A = mult * R([random.choice(els) for _ in range(b)] + [one]); lam = random.choice(els[1:]); a = A.degree()
            r = nfac(lam*A**4 - Q); rQ = nfac(Q)
            st[(r - rQ - 1 - k*a) % 2] += 1
        print("F_%d d=4 q3=0, %s:" % (q, name), sorted(st.items()))

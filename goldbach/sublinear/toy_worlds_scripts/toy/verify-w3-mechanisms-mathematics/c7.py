import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(7)
for k in (1,2,3,4):
    q = 2**k
    F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; zero=F(0); one=F(1)
    def tr(v):
        s = zero; w = v
        for _ in range(k): s += w; w = w*w
        return 0 if s == zero else 1
    def nfac(f): return sum(m for _, m in f.factor()[1])
    st = Counter()
    for t in range(1500):
        q0, q1, q2 = random.choice(els), random.choice(els[1:]), random.choice(els)
        Q = R([q0, q1, q2, zero, one])
        a = random.randint(2, 7)   # n-d>=4
        A = R([random.choice(els) for _ in range(a)] + [one]); lam = random.choice(els[1:])
        r = nfac(lam*A**4 - Q); rQ = nfac(Q)
        st[(r - rQ - 1 - k*a - tr(q2**3/q1**2)) % 2] += 1
    print("F_%d d=4 q3=0: r - r(Q) - 1 - k a - Tr(q2^3/q1^2) mod 2:" % q, sorted(st.items()))

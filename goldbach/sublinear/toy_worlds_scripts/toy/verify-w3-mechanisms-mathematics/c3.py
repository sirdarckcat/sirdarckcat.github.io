# (c) test candidate rule for d=4, q_3=0 : r(N-Q) = r(Q)+1+k*a mod 2 ?
import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(3)
for k in (1,2,3,4):
    q = 2**k
    F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; zero=F(0); one=F(1)
    def nfac(f): return sum(m for _, m in f.factor()[1])
    st = Counter()
    for t in range(1500):
        Q = R([random.choice(els), random.choice(els[1:]), random.choice(els), zero, one])
        if Q.gcd(Q.derivative()).degree() != 0: continue
        a = random.randint(2, 6)
        A = R([random.choice(els) for _ in range(a)] + [one]); lam = random.choice(els[1:])
        r = nfac(lam*A**4 - Q); rQ = nfac(Q)
        st[(r - rQ - 1 - k*a) % 2] += 1
    print("F_%d d=4 q3=0: (r - r(Q) - 1 - k a) mod 2 counts" % q, dict(st))

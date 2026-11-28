# outside Theorem 1: d even with Q' a nonzero constant (q_{d-1} = 0 ...). Test guess r(N-Q) = r(Q) + 1 + k*a + k*e(d) mod 2
import random
from ff2 import W
rng = random.Random(4)
res = {}
for k in (1,2,3,4):
    w = W(k); F = w.F
    for t in range(1500):
        d = rng.choice([2,4,6,8])
        c = [F(0)]*(d+1); c[d] = F(1)
        for i in range(0, d, 2): c[i] = rng.choice(w.els)
        c[1] = rng.choice(w.els[1:])
        Q = w.R(c)
        if not Q.is_squarefree(): continue
        a = rng.randint(d//4 + 1, d//4 + 6)
        A = w.rand_monic(a, rng); lam = rng.choice(w.els[1:])
        f = lam*A**4 - Q
        rf, sqf = w.nfac(f); rQ, _ = w.nfac(Q)
        assert sqf
        delta = (rf - rQ - 1 - k*a) % 2
        key = (k, d, 4*a - d >= 4)
        e = res.setdefault(key, [0,0]); e[delta] += 1
for key in sorted(res): print("k, d, n-d>=4:", key, " r(N-Q) - r(Q) - 1 - k*a mod 2 = [0,1] counts:", res[key])

# Q' = nonzero constant, d even: is r(lam A^4 - Q) - k*a mod 2 a function of (d, n-d) only (independent of Q, r(Q))?
import random
from ff2 import W
rng = random.Random(41)
res = {}
for k in (1,2,3,4):
    w = W(k); F = w.F
    for t in range(2500):
        d = rng.choice([4,6,8,10,12])
        c = [F(0)]*(d+1); c[d] = F(1)
        for i in range(0, d, 2): c[i] = rng.choice(w.els)
        c[1] = rng.choice(w.els[1:])
        Q = w.R(c)
        a = rng.randint(d//4 + 1, d//4 + 5)
        A = w.rand_monic(a, rng); lam = rng.choice(w.els[1:])
        f = lam*A**4 - Q
        rf, sqf = w.nfac(f)
        assert sqf
        key = (k, d, min(4*a - d, 8))
        e = res.setdefault(key, [0,0]); e[(rf - k*a) % 2] += 1
for key in sorted(res): print("k, d, min(n-d,8):", key, " r(N-Q) - k*a mod 2 = [0,1] counts:", res[key])

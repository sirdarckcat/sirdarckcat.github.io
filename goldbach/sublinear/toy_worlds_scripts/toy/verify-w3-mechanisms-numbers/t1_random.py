# Theorem 1: adversarial random test. A = S*B with B random (NOT a multiple of L_J), Q random monic squarefree
# (mostly reducible), lam random, small n-d included.
import sys, random
from ff2 import W, predicted
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
ntr = int(sys.argv[1])
tot = 0; bad = 0; byk = {}
edge = {}   # hypotheses violated: (label) -> [agree, disagree] with the naive formula
for k in (1,2,3,4,5):
    w = W(k); F = w.F
    cnt = 0; b = 0
    for t in range(ntr):
        d = rng.randint(1, 9 if k <= 2 else 6)
        Q = w.rand_monic(d, rng)
        if not Q.is_squarefree(): continue
        S = w.S_of(Q)
        if S.is_zero(): continue
        smin = S.degree()
        # choose a so that n=4a > d ; allow n-d as small as possible sometimes
        amin = max(smin, d//4 + 1, 1)
        a = amin + rng.choice([0,0,1,2,3,rng.randint(0,8)])
        B = w.rand_monic(a - smin, rng)
        Sm = S * S.leading_coefficient()**(-1) if hasattr(S.leading_coefficient(), '__pow__') else S
        A = Sm * B
        assert A.degree() == a and A.is_monic()
        lam = rng.choice(w.els[1:])
        N = lam * A**4
        f = N - Q
        rQ, _ = w.nfac(Q)
        rf, sqf = w.nfac(f)
        assert sqf, "N-Q not squarefree"
        pr = predicted(w, lam, A, Q, rQ)
        n = 4*a; c = Q.coeffs()
        if pr is None:
            # record behaviour outside the hypotheses, using the naive even-d formula
            if d % 2 == 0 and c[d-1] != F(0) and n - d < 4:
                if d % 4 == 0: naive = (rQ + k*(a + d//4)) % 2
                else: naive = (rQ + k*(a + (d-2)//4) + w.tr(c[d-2]/(c[d-1]*c[d-1]))) % 2
                e = edge.setdefault(('n-d<4', k), [0,0]); e[0 if naive == rf % 2 else 1] += 1
            continue
        cnt += 1
        if pr != rf % 2:
            b += 1
            print("BAD", k, lam, A, Q, rf, rQ)
    byk[k] = (cnt, b); tot += cnt; bad += b
print("Theorem 1 random test, per k (checks, disagreements):", byk, "total", tot, "bad", bad)
print("outside hypothesis n-d>=4 (d even, q_{d-1}!=0), naive formula [agree, disagree]:", edge)

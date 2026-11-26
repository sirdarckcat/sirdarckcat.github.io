# Beyond complete enumeration: the translation-invariant family F_q[x^p - x] (q prime, p | n) searched exhaustively,
# against a random sample of all monic N of the same degree.  D(N) = degree of the first row Q (degree, then index)
# with N - Q irreducible.  Root law: P_family(D >= d) ~ P_all(D >= d)^(1/p).
#   python3 family_big.py q n samples maxrowdeg
import sys, random, itertools, collections, math, time
from gfcommon import World
q, n, S, md = (int(v) for v in sys.argv[1:5]); W = World(q); p = W.p; x = W.x; random.seed(12345)
t0 = time.time(); rows = W.rows(md); nb = collections.Counter(Q.degree() for Q in rows)
def D_of(N):
    for i, Q in enumerate(rows):
        if (N - Q).is_irreducible(): return Q.degree(), i
    return md + 1, len(rows)
y = x ** p - x; m = n // p
fam = []
for cs in itertools.product(W.el, repeat=m):
    N = y ** m
    for k, c in enumerate(cs): N = N + c * y ** k
    fam.append((D_of(N), N))
tf = time.time() - t0
smp = collections.Counter()
for _ in range(S):
    N = W.poly(random.randrange(q ** n), n); smp[D_of(N)[0]] += 1
print(f"q={q} n={n}: family F_q[x^p-x]: {len(fam)} members ({tf:.0f}s); random sample {S} of q^n = {q ** n:.3e}; rows to degree {md} ({len(rows)})")
best = max(fam, key=lambda t: (t[0][0], t[0][1]))
print(f"  best family member: D = {best[0][0]}{'+' if best[0][0] > md else ''}, G = {best[0][1]}: N = {best[1]}")
for d in range(2, md + 2):
    F = sum(1 for (dd, g), N in fam if dd >= d); K = sum(v for dd, v in smp.items() if dd >= d)
    if F == 0 and K == 0: break
    rate = K / S
    pred = len(fam) * rate ** (1 / p) if K else float('nan')
    impl = (F / len(fam)) ** p if F else 0
    print(f"  D >= {d}: family {F:>6} of {len(fam)} ({F / len(fam):.3e}); sample {K:>7} of {S} ({rate:.3e}); root-law prediction for the family {pred:8.1f};"
          f" (family rate)^p = {impl:.3e} => expected number among all q^n: {impl * q ** n:.3g}")

# q = 9: the coefficient Frobenius s (c -> c^3) is a ring automorphism of F_9[x] fixing N in F_3[x]; N - Q^s = (N - Q)^s.
# Family: the 3^n monic N with coefficients in F_3.  Rows: 9 linear (3 fixed, 3 pairs), 36 quadratics (18 pairs).
import re, itertools
from fam import world, rows_upto, GD, poly
q = 9; p, F, R, x, el = world(q)
rows = rows_upto(R, F, el, q, 3)
frob = lambda Q: R([c ** 3 for c in Q.coeffs()])
fx = {}
for Q in rows:
    d = Q.degree(); fx.setdefault(d, [0, 0]); fx[d][0] += 1; fx[d][1] += (frob(Q) == Q)
print("rows by degree [count, Frobenius-fixed]:", fx)
K = {}
for fn in ("enum_small.txt", "enum_mid.txt", "enum_big.txt"):
    L = open(fn).read().split("\n")
    for i, s in enumerate(L):
        m = re.match(r"q 9 n (\d+) ", s)
        if m: K[int(m.group(1))] = {int(a): int(b) for a, b in re.findall(r"(\d+):(\d+)", L[i + 2])}
f3 = [F(0), F(1), F(2)]
bad = 0
for n in range(5, 10):
    tot = 9 ** n; cnt = {2: 0, 3: 0, 4: 0}; best = (0, None)
    for cs in itertools.product(f3, repeat=n):
        N = R(list(cs) + [F(1)])
        g, d = GD(N, rows, n)
        for dd in cnt: cnt[dd] += d >= dd
        if g > best[0]: best = (g, N)
        # orbit check on a few
    k2 = K[n].get(2, 0); k3 = K[n].get(3, 0)
    b1 = k2 / tot; b2 = k3 / k2 if k2 else 0
    print(f"(9,{n}): rational N: {3**n}; D>=2: {cnt[2]} (root h=2: {3**n * b1 ** 0.5:.1f}; orbit-count 6/9: {3**n * b1 ** (6/9):.1f}; plain rate: {3**n * b1:.1f});"
          f" D>=3: {cnt[3]} (root: {3**n * (b1*b2) ** 0.5:.1f}; orbit-count: {3**n * b1 ** (6/9) * b2 ** 0.5:.1f}; plain rate: {3**n * b1 * b2:.2f}); all N with D>=3: {k3}; best G (rows deg<=3) {best}")
# direct check of the lemma
import random
random.seed(5); mism = 0; tested = 0
for _ in range(300):
    n = random.randint(4, 9); N = R([random.choice(f3) for _ in range(n)] + [F(1)])
    for Q in random.sample(rows, 20):
        t1 = sorted((g.degree(), m) for g, m in (N - Q).factor()[1]); t2 = sorted((g.degree(), m) for g, m in (N - frob(Q)).factor()[1])
        tested += 1; mism += t1 != t2
print("Frobenius orbit lemma: tested", tested, "type mismatches", mism)

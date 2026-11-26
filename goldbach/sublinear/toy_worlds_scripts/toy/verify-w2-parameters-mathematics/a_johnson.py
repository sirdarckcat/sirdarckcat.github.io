import sys, math, random, itertools, time
sys.path.insert(0, "/tmp/claude-0/-home-user-sirdarckcat-github-io/9ab28896-d478-5e7c-817b-7f69ce9b4074/scratchpad/work/toy/w2-parameters")
import numpy as np
import w2core as w

# 1. M_n(D) formula and the two bounds
bad = 0
for n in range(2, 9):
    for D in range(1, 200):
        br = sum(1 for b in range(0, D) for a in range(0, D) if a + (n - 1) * b < D)
        M = w.count_monomials(n, D)
        if br != M: bad += 1
        if not (D * D / (2 * (n - 1)) <= M <= (D + (n - 1) / 2) ** 2 / (2 * (n - 1)) + 1e-9): bad += 1
print("M_n(D) formula / bounds violations:", bad)

# 2. Abundant consistent sets INSIDE the Johnson guarantee (random lists, nothing planted)
def run(q, n, l, s, trials, seed):
    rng = random.Random(seed)
    places = w.irreducibles(q, 1)
    m = len(places)
    D = m * s
    C = m * l * s * (s + 1) // 2
    M = w.count_monomials(n, D)
    J = (D - 1) // (n - 1)
    E = q ** n * (l / q) ** m
    print(f"q={q} points={m} l={l} n={n} s={s}: D={D} C={C} M={M} guarantee={M > C} J={J} q^n={q**n} E|C(L)|={E:.2f}")
    for t in range(trials):
        L = w.random_lists(q, places, [l] * m, rng)
        cons, _ = w.consistent(q, n, places, L)
        t0 = time.time()
        A, mons = w.interpolation_matrix(q, n, D, places, L, [s] * m)
        rank, basis = w.kernel(q, A)
        # common y-roots of the whole kernel
        roots = None
        for vec in basis[:6]:
            r = set(w.y_roots(q, n, mons, vec))
            roots = r if roots is None else roots & r
        print(f"   trial {t}: |C(L)|={len(cons)} kernel dim={len(basis)} common roots of (first 6) kernel vectors={len(roots)} equal={set(cons.tolist()) == roots}  ({time.time()-t0:.1f}s)")

run(5, 2, 4, 4, 6, 1)
run(7, 2, 6, 6, 3, 2)
run(13, 2, 12, 12, 1, 3)

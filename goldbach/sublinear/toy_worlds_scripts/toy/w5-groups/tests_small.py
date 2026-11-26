#!/usr/bin/env python3
"""Exhaustive checks of the page's statements on small instances (every claim checked against brute force).
T1  k best of a product: heap listing = sorted brute force (scores), <= 3 pushes per pop.
T2  the arc: for every x in [0,P): frac(sum x_r u_r / r) = x/P exactly (Fractions).
T3  rounded DP: [0,X) subset R subset [0, X + mP/B) u [P - mP/B, P); min over R correct; listing of R by score complete;
    the feasible ones among the listed = brute-force best of [0,X); nodes visited <= (m+1) * outputs + targets.
T4  exact trellis: number of distinct nonempty completion sets at a cut (deterministic width) and the fooling set {0..n-1}.
T5  rectangle bound and strip bound: inequalities of the lower-bound proof checked on maximal rectangles found by search.
T6  rank-two Bohr set {x/P in [0,d1), g x/P in [0,d2)}: the product-state DP (B1*B2 states) has the sandwich property and the exact minimum over its relaxed set.
"""
import random, math, itertools, sys
from fractions import Fraction
import w5lib as L
rnd = random.Random(5)
def all_points(mods): return itertools.product(*[range(r) for r in mods])

# ---- T1
bad = 0; tot = 0; maxratio = 0
for trial in range(300):
    m = rnd.randint(1, 5); sizes = [rnd.randint(1, 6) for _ in range(m)]
    tables = [[rnd.randint(0, 6) for _ in range(r)] for r in sizes]
    allp = sorted(sum(t[c] for t, c in zip(tables, x)) for x in all_points(sizes))
    k = rnd.randint(1, len(allp))
    out, pushes = L.kbest_product(tables, k)
    ok = [s for s, _ in out] == allp[:k] and len(set(x for _, x in out)) == k and all(sum(t[c] for t, c in zip(tables, x)) == s for s, x in out)
    bad += not ok; tot += 1; maxratio = max(maxratio, pushes / k)
print(f"T1 k best of a product: {tot} random instances, {bad} failures; max pushes per output {maxratio:.2f} (bound 3)")

# ---- T2
cnt = 0
for mods in ([3, 5, 7, 11], [2, 3, 5, 7, 11, 13], [4, 9, 5, 7], [7, 11, 13, 17]):
    P, u = L.arc_data(mods)
    for x in range(P):
        f = sum(Fraction((x % r) * ui, r) for r, ui in zip(mods, u)); f -= math.floor(f)
        assert f == Fraction(x, P); cnt += 1
print(f"T2 arc identity frac(sum x_r u_r/r) = x/P: {cnt} integers over 4 sets of moduli, all exact")

# ---- T3
fails = 0; runs = 0; worst_over = 0; tot_listed = 0; tot_feasible = 0; maxnodes = 0
for trial in range(60):
    mods = rnd.sample([3, 5, 7, 11, 13], rnd.randint(3, 4)); m = len(mods); P, u = L.arc_data(mods)
    X = rnd.randint(max(2, P // 200), P // 2)
    tables = [[rnd.randint(0, 9) for _ in range(r)] for r in mods]
    eps = rnd.choice([1.0, 0.5, 0.25]); B = math.ceil(m * P / (eps * X))
    rho, V, targets = L.rounded_dp(mods, tables, X, B)
    S = lambda x: sum(t[x % r] for t, r in zip(tables, mods))
    score = [S(x) for x in range(P)]
    # membership of R by definition
    inR = [(sum(rho[i][x % mods[i]] for i in range(m)) % B) in set(targets) for x in range(P)]
    ok = all(inR[x] for x in range(X))                                                   # [0,X) inside R
    slack = Fraction(m * P, B)
    ok &= all((x < X + slack or x >= P - slack) for x in range(P) if inR[x])             # R inside the widened arc
    ok &= slack <= eps * X
    bestR = min(score[x] for x in range(P) if inR[x]); ok &= bestR == min(V[m][b] for b in targets)
    theta = sorted(score[x] for x in range(X))[min(X - 1, 20)]                           # the 21st best feasible score
    listed, nodes = L.list_relaxed(mods, tables, rho, V, targets, theta)
    ints = sorted(L.crt_int(mods, x) for x in listed)
    ok &= ints == sorted(x for x in range(P) if inR[x] and score[x] <= theta)            # listing complete and exact
    feas = sorted(x for x in ints if x < X); ok &= feas == sorted(x for x in range(X) if score[x] <= theta)
    ok &= nodes <= (m + 1) * len(listed) + len(targets)
    maxnodes = max(maxnodes, nodes / max(1, len(listed)))
    tot_listed += len(ints); tot_feasible += len(feas); worst_over = max(worst_over, len(ints) / max(1, len(feas)))
    fails += not ok; runs += 1
print(f"T3 rounded DP: {runs} random instances, {fails} failures; listed {tot_listed}, of them below X {tot_feasible} "
      f"(ratio {tot_listed / tot_feasible:.3f}; worst instance {worst_over:.2f}); nodes visited per listed point at most {maxnodes:.2f}")

# ---- T4
print("T4 exact trellis width at a cut (prefix = first t moduli), and the fooling set; X <= P/2")
for mods, X in (([3, 5, 7, 11, 13], 1000), ([3, 5, 7, 11, 13], 7000), ([13, 11, 7, 5, 3], 300), ([5, 7, 11, 13, 17], 40000), ([7, 3, 13, 5, 11, 2], 2000)):
    P, u = L.arc_data(mods); m = len(mods); line = []
    assert X <= P // 2
    for t in range(1, m):
        PI = math.prod(mods[:t]); PC = P // PI
        comp = {}
        for x in range(X): comp.setdefault(x % PI, []).append(x % PC)
        width = len({tuple(sorted(v)) for v in comp.values()})
        n = min(PI, PC, X)
        # fooling set {0..n-1}: for x != y not both crossings are below X
        cross = lambda a, c: (a * PC * pow(PC, -1, PI) + c * PI * pow(PI, -1, PC)) % P
        fool = all(not (cross(x % PI, y % PC) < X and cross(y % PI, x % PC) < X) for x in range(n) for y in range(x + 1, n)) if n <= 400 else None
        line.append(f"t={t}: P_I={PI}, P_Ic={PC}, det. width {width}, min(P_I,P_Ic,X)={n}, fooling {fool}")
    print(f"  moduli {mods}, X={X}, P={P}, e^D={P / X:.1f}\n    " + "\n    ".join(line))

# ---- T5
print("T5 rectangles inside the widened arc: |A||C| against the bound; strip: points of the top strip that can share a rectangle with a given one")
def check_rect(mods, t, X, eps, tries=300):
    P, u = L.arc_data(mods); PI = math.prod(mods[:t]); PC = P // PI
    E = int(eps * X); lam = 1 + 2 * eps; delta = Fraction(X, P)
    assert 2 * (X + 2 * E) <= P
    inR = lambda z: z < X + E or z >= P - E                # the largest admissible R
    eI = PC * pow(PC, -1, PI); eC = PI * pow(PI, -1, PC)
    cross = lambda a, c: (a * eI + c * eC) % P
    rowsets = {}                                            # a -> set of c with (a,c) in R
    for z in list(range(0, X + E)) + list(range(P - E, P)): rowsets.setdefault(z % PI, set()).add(z % PC)
    Lam = X + 2 * E; bound = Lam * Lam / (4 * P) + Lam / min(PI, PC) + 1
    best = 0
    keys = list(rowsets)
    for _ in range(tries):
        a0 = rnd.choice(keys); C = set(rowsets[a0])
        # grow greedily: add rows, shrinking C, keeping the product large
        A = [a0]; cur = len(C)
        cand = rnd.sample(keys, min(len(keys), 60))
        cand.sort(key=lambda a: -len(C & rowsets[a]))
        for a in cand:
            if a in A: continue
            C2 = C & rowsets[a]
            if len(C2) * (len(A) + 1) >= cur: C = C2; A.append(a); cur = len(C) * len(A)
        Afull = [a for a in keys if C <= rowsets[a]]        # close up
        best = max(best, len(Afull) * len(C))
        assert len(Afull) * len(C) <= bound + 1e-9, (len(Afull), len(C), bound)
    # strip: the top E integers below X; partners of x = strip points y with both crossings in R
    n = E; strip = range(X - n, X)
    assert E >= 1 and 2 * X + 3 * E <= P
    sb = min((5 * E / PC + 1) * (2 * E / PI + 1), (5 * E / PI + 1) * (2 * E / PC + 1))
    mx = 0
    for x in rnd.sample(list(strip), min(n, 60)):
        comp = sum(1 for y in strip if inR(cross(x % PI, y % PC)) and inR(cross(y % PI, x % PC)))
        mx = max(mx, comp); assert comp <= sb + 1e-9, (comp, sb)
    w1 = X / bound; w2 = n / sb
    return PI, PC, best, bound, mx, sb, w1, w2
for mods, t, X, eps in (([3, 5, 7, 11, 13, 17], 3, 6000, 0.25), ([3, 5, 7, 11, 13, 17], 3, 2000, 0.5), ([3, 5, 7, 11, 13, 17], 3, 20000, 0.1),
                        ([3, 5, 7, 11, 13, 17], 2, 6000, 0.25), ([5, 7, 11, 13, 17, 19], 3, 30000, 0.05), ([5, 7, 11, 13, 17, 19], 3, 3000, 1.0)):
    P = math.prod(mods)
    PI, PC, best, bound, mx, sb, w1, w2 = check_rect(mods, t, X, eps)
    m = len(mods)
    print(f"  moduli {mods} cut {t} (P_I={PI}, P_Ic={PC}), X={X}, e^D={P / X:.1f}, eps={eps}: largest rectangle found {best} <= bound {bound:.1f}; "
          f"strip partners {mx} <= {sb:.1f}; states needed >= max({w1:.1f}, {w2:.1f}); the DP uses B = {math.ceil(m * P / (eps * X))}")

# ---- T6
fails = 0; runs = 0; st = []
for trial in range(25):
    mods = rnd.sample([3, 5, 7, 11, 13], 4); m = 4; P, u = L.arc_data(mods)
    g = rnd.choice([x for x in range(2, P) if math.gcd(x, P) == 1])
    X1 = rnd.randint(P // 20, P // 3); X2 = rnd.randint(P // 20, P // 3)
    tables = [[rnd.randint(0, 9) for _ in range(r)] for r in mods]
    B1 = math.ceil(m * P / X1); B2 = math.ceil(m * P / X2)                      # eps = 1 in both characters
    r1 = [[(B1 * ((c * ui) % r)) // r for c in range(r)] for ui, r in zip(u, mods)]
    r2 = [[(B2 * ((g * c * ui) % r)) // r for c in range(r)] for ui, r in zip(u, mods)]
    cur = {(0, 0): 0}
    for t in range(m):
        nxt = {}
        for (b1, b2), v in cur.items():
            for c in range(mods[t]):
                key = ((b1 + r1[t][c]) % B1, (b2 + r2[t][c]) % B2); w = v + tables[t][c]
                if w < nxt.get(key, 1e9): nxt[key] = w
        cur = nxt
    T1 = {b % B1 for b in range(-(m - 1), -((-B1 * X1) // P))}; T2 = {b % B2 for b in range(-(m - 1), -((-B2 * X2) // P))}
    dpmin = min((v for (b1, b2), v in cur.items() if b1 in T1 and b2 in T2), default=None)
    S = lambda x: sum(t[x % r] for t, r in zip(tables, mods))
    inR = lambda x: (sum(r1[i][x % mods[i]] for i in range(m)) % B1) in T1 and (sum(r2[i][x % mods[i]] for i in range(m)) % B2) in T2
    bohr = [x for x in range(P) if x < X1 and (g * x) % P < X2]
    Rset = [x for x in range(P) if inR(x)]
    wid = lambda x: (x < 2 * X1 or x >= P - X1) and ((g * x) % P < 2 * X2 or (g * x) % P >= P - X2)
    ok = set(bohr) <= set(Rset) and all(wid(x) for x in Rset) and dpmin == min(S(x) for x in Rset)
    fails += not ok; runs += 1; st.append((B1 * B2, P * P / (X1 * X2), len(Rset) / max(1, len(bohr))))
print(f"T6 rank-two Bohr sets: {runs} random instances, {fails} failures; states B1*B2 = (m/eps)^2 * P^2/(X1 X2) (m = 4, eps = 1: ratio {sum(a / b for a, b, c in st) / len(st):.1f}); "
      f"|R| / |Bohr set| on average {sum(c for a, b, c in st) / len(st):.2f}")

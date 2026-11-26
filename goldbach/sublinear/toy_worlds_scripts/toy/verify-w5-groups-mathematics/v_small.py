#!/usr/bin/env python3
"""Independent small-case checks of the w5-groups page (own code, nothing imported from the page)."""
import itertools, math, random, heapq, sys
from fractions import Fraction
rnd = random.Random(20261126)

def crt_pair(PI, PC):
    P = PI * PC
    eI = PC * pow(PC, -1, PI); eC = PI * pow(PI, -1, PC)
    return P, (lambda a, c: (a * eI + c * eC) % P)

# ------------------------------------------------------------------ Theorem 1(b): the tree, as stated
def t1():
    bad_parent = bad_mono = bad_order = 0; inst = 0; maxpush = 0
    for trial in range(400):
        m = rnd.randint(1, 5); sizes = [rnd.randint(1, 5) for _ in range(m)]
        tabs = [sorted(rnd.choice([0, 0, 1, 2, 3, 5]) for _ in range(r)) for r in sizes]   # sorted tables, many ties
        gap = [t[1] - t[0] if len(t) > 1 else math.inf for t in tabs]
        order = sorted(range(m), key=lambda i: gap[i]); tabs = [tabs[i] for i in order]; sizes = [sizes[i] for i in order]
        mm = sum(1 for r in sizes if r > 1)             # coordinates with a choice come first (finite gaps)
        S = lambda x: sum(t[c] for t, c in zip(tabs, x))
        def children(x):
            nz = [i for i in range(m) if x[i]]
            ch = []
            if not nz:
                if mm >= 1: y = list(x); y[0] = 1; ch.append(tuple(y))
                return ch
            t = nz[-1]; p = x[t]
            if p + 1 < sizes[t]: y = list(x); y[t] = p + 1; ch.append(tuple(y))
            if t + 1 < mm:
                y = list(x); y[t + 1] = 1; ch.append(tuple(y))
                if p == 1: y = list(x); y[t] = 0; y[t + 1] = 1; ch.append(tuple(y))
            return ch
        pts = list(itertools.product(*[range(r) for r in sizes]))
        par = {}
        for x in pts:
            for y in children(x):
                if S(y) < S(x): bad_mono += 1
                par.setdefault(y, []).append(x)
        root = tuple([0] * m)
        for x in pts:
            if x == root: bad_parent += (x in par)
            else: bad_parent += (len(par.get(x, [])) != 1)
        # heap listing
        heap = [(S(root), root)]; out = []; pushes = 1
        while heap:
            s, x = heapq.heappop(heap); out.append(s)
            for y in children(x): heapq.heappush(heap, (S(y), y)); pushes += 1
        bad_order += out != sorted(S(x) for x in pts); inst += 1; maxpush = max(maxpush, pushes / len(out))
    print(f"T1 tree of Theorem 1(b): {inst} instances (ties allowed): parent-uniqueness failures {bad_parent}, monotonicity failures {bad_mono}, "
          f"listing-order failures {bad_order}, pushes per output <= {maxpush:.2f}")

# ------------------------------------------------------------------ Theorem 3(i) with a general base point y and E < m
def t3():
    fails_in = fails_out = runs = 0; nonvac = 0
    for trial in range(300):
        mods = rnd.sample([3, 5, 7, 11, 13, 4, 9], rnd.randint(3, 4))
        ok = all(math.gcd(a, b) == 1 for a, b in itertools.combinations(mods, 2))
        if not ok: continue
        m = len(mods); P = math.prod(mods); u = [pow(P // r % r, -1, r) for r in mods]
        X = rnd.randint(1, P); ny = rnd.randrange(P); y = [ny % r for r in mods]
        E = rnd.randint(1, m); B = rnd.randint(1, 3 * P // X * E + 5)
        rho = [[(B * (((c - y[i]) * u[i]) % mods[i])) // mods[i] for c in range(mods[i])] for i in range(m)]
        lo = math.floor(Fraction(-B * ny, P) - E) + 1; hi = math.ceil(Fraction(B * (X - ny), P)) - 1     # integers of the open interval
        T = {n % B for n in range(lo, hi + 1)}
        for x in range(P):
            off = sum(1 for i in range(m) if x % mods[i] != y[i])
            if off > E: continue
            inR = (sum(rho[i][x % mods[i]] for i in range(m)) % B) in T
            if x < X and not inR: fails_in += 1
            if inR:
                # x/P mod 1 in (-E/B, X/P + E/B)
                f = Fraction(x, P)
                good = f < Fraction(X, P) + Fraction(E, B) or f - 1 > -Fraction(E, B)
                fails_out += not good; nonvac += 1
        runs += 1
    print(f"T3(i) general base, E <= m, arbitrary B >= 1: {runs} instances, inclusion failures {fails_in}, sandwich failures {fails_out} ({nonvac} points of R checked)")

# ------------------------------------------------------------------ Theorem 4(a): fooling set, all cuts (not only prefixes), X up to P/2 and beyond
def t4a():
    viol = 0; cuts = 0; viol_beyond = 0; cuts_beyond = 0
    for mods in ([3, 5, 7, 11], [2, 3, 5, 7, 11], [4, 9, 5, 7], [3, 5, 7, 11, 13]):
        P = math.prod(mods); m = len(mods)
        for mask in range(1, 2 ** m - 1):
            PI = math.prod(mods[i] for i in range(m) if mask >> i & 1); PC = P // PI
            _, cross = crt_pair(PI, PC)
            for X in sorted({2, 3, P // 7, P // 3, P // 2 - 1, P // 2, (P + 1) // 2, P // 2 + 1, 2 * P // 3, P - 1}):
                if X < 1: continue
                n = min(PI, PC, X)
                if n > 300: continue
                bad = any(cross(x % PI, y % PC) < X and cross(y % PI, x % PC) < X for x in range(n) for y in range(x + 1, n))
                if 2 * X <= P: cuts += 1; viol += bad
                else: cuts_beyond += 1; viol_beyond += bad
    print(f"T4(a) fooling set {{0..n-1}}, n = min(P_I,P_Ic,X): {cuts} (cut, X) pairs with 2X <= P, violations {viol}; "
          f"with 2X > P: {cuts_beyond} pairs, fooling property fails in {viol_beyond} (the hypothesis X <= P/2 is used)")

# ------------------------------------------------------------------ Theorem 4(b), 4(c) and my bound (c'): exhaustive over all subsets A of the small side
def rect_exhaust(PI, PC, X, E0):
    """R_max = [-E0, X+E0) mod P.  Enumerate every subset A of Z/PI (PI <= 16), C(A) = all c with A x {c} inside R_max.
    Returns max |A||C|, max number of points of the top strip [X-E0, X) in a rectangle, max number of points of [0,X) in a rectangle."""
    P, cross = crt_pair(PI, PC)
    inR = lambda z: z < X + E0 or z >= P - E0
    rowmask = []                                       # for each a: bitmask over c
    for a in range(PI):
        mk = 0
        for c in range(PC):
            if inR(cross(a, c)): mk |= 1 << c
        rowmask.append(mk)
    stripmask = [0] * PI; intmask = [0] * PI
    for x in range(X):
        intmask[x % PI] |= 1 << (x % PC)
        if x >= X - E0: stripmask[x % PI] |= 1 << (x % PC)
    full = (1 << PC) - 1
    best_area = best_strip = best_int = 0
    # Gray-code free DFS with pruning on empty C
    def rec(i, cm, size, sm_list):
        nonlocal best_area, best_strip, best_int
        if cm == 0: return
        if i == PI:
            if size:
                best_area = max(best_area, size * bin(cm).count("1"))
                best_strip = max(best_strip, sum(bin(stripmask[a] & cm).count("1") for a in sm_list))
                best_int = max(best_int, sum(bin(intmask[a] & cm).count("1") for a in sm_list))
            return
        rec(i + 1, cm & rowmask[i], size + 1, sm_list + [i])
        rec(i + 1, cm, size, sm_list)
    rec(0, full, 0, [])
    return best_area, best_strip, best_int
def t4bc():
    print("T4(b),(c): EXHAUSTIVE maximum over all rectangles inside R_max = [-E0, X+E0) (every subset A of the side of size P_I)")
    worst_b = worst_c = worst_n = 0; nb = nc = nn = 0; viol_c_big = 0
    cases = []
    for (PI, PC) in ((15, 77), (14, 195), (13, 105), (11, 105), (15, 1001), (16, 315)):
        P = PI * PC
        for X in sorted({P // 40, P // 20, P // 12, P // 8}):
            for eps in (0.1, 0.25, 0.5, 1.0, 2.0, 3.0):
                E0 = int(eps * X)
                if X < 2: continue
                cases.append((PI, PC, X, E0, eps))
    for (PI, PC, X, E0, eps) in cases:
        P = PI * PC; Lam = X + 2 * E0
        if (X + 2 * E0) * 3 > P: continue
        area, strip, inter = rect_exhaust(PI, PC, X, E0)
        if 2 * Lam <= P:
            bound = Lam * Lam / (4 * P) + Lam / min(PI, PC) + 1
            nb += 1; worst_b = max(worst_b, area / bound)
            if area > bound + 1e-9: print("   VIOLATION of 4(b):", PI, PC, X, E0, area, bound)
        if E0 >= 1 and 2 * X + 3 * E0 <= P and E0 <= X:
            sb = min((5 * E0 / PC + 1) * (2 * E0 / PI + 1), (5 * E0 / PI + 1) * (2 * E0 / PC + 1))
            nc += 1; worst_c = max(worst_c, strip / sb)
            if strip > sb + 1e-9: print("   VIOLATION of 4(c):", PI, PC, X, E0, strip, sb)
        if 3 * X + 2 * E0 <= P:
            nbnd = min((2 * (X + E0) / PC + 1) * (2 * X / PI + 1), (2 * (X + E0) / PI + 1) * (2 * X / PC + 1))
            nn += 1; worst_n = max(worst_n, inter / nbnd)
            if inter > nbnd + 1e-9: print("   VIOLATION of (c'):", PI, PC, X, E0, inter, nbnd)
    print(f"   4(b): {nb} cases, max area / bound = {worst_b:.3f};  4(c) (with E0 <= X): {nc} cases, max strip points in a rectangle / bound = {worst_c:.3f};")
    print(f"   (c') points of [0,X) in one rectangle <= (2(X+E0)/P_Ic+1)(2X/P_I+1) (min with I, Ic exchanged): {nn} cases, max ratio {worst_n:.3f}")

# ------------------------------------------------------------------ Theorem 4(c) as stated, with E0 > X: is the conclusion false?
def t4c_counter():
    # w([0,X)) <= X always (singletons).  The stated bound E0/((5E0/P_Ic+1)(2E0/P_I+1)) with E0 > X and P_I, P_Ic large exceeds X.
    PI, PC = 1009, 1013; P = PI * PC
    X = 10; E0 = 30                                   # "E0 = floor(eps X)" with eps = 3; E0 >= 1 and 2X + 3E0 = 110 <= P
    stated = E0 / ((5 * E0 / PC + 1) * (2 * E0 / PI + 1))
    print(f"T4(c) hypothesis: P_I={PI}, P_Ic={PC}, X={X}, E0={E0} (eps=3), 2X+3E0={2 * X + 3 * E0} <= P={P}: stated lower bound {stated:.2f} > X = {X} >= w([0,X)) "
          f"-> the statement needs E0 <= X (the strip must lie inside [0,X))")

# ------------------------------------------------------------------ Theorem 5(a): w(ker psi) = |im psi_I meet im psi_Ic| on small groups with repeated primes
def t5a():
    ok = 0; tot = 0
    for trial in range(200):
        p = rnd.choice([2, 3]); n = rnd.randint(3, 6); k = rnd.randint(1, 3)
        H = [[rnd.randrange(p) for _ in range(n)] for _ in range(k)]         # psi : (Z/p)^n -> (Z/p)^k, x -> Hx
        t = rnd.randint(1, n - 1)
        def img(cols):
            im = set()
            for x in itertools.product(range(p), repeat=len(cols)):
                im.add(tuple(sum(H[r][c] * xi for c, xi in zip(cols, x)) % p for r in range(k)))
            return im
        imI = img(list(range(t))); imC = img(list(range(t, n))); imAll = img(list(range(n)))
        # rectangles of the kernel: classes of (psi_I = q) x (psi_Ic = -q), q in the intersection
        inter = imI & {tuple((-v) % p for v in q) for q in imC}
        # deterministic width: number of distinct nonempty completion sets
        comp = {}
        for a in itertools.product(range(p), repeat=t):
            qa = tuple(sum(H[r][c] * a[c] for c in range(t)) % p for r in range(k))
            cs = frozenset(c for c in itertools.product(range(p), repeat=n - t)
                           if all((qa[r] + sum(H[r][t + i] * c[i] for i in range(n - t))) % p == 0 for r in range(k)))
            if cs: comp.setdefault(cs, []).append(a)
        width = len(comp)
        formula = len(imI) * len(imC) // len(imAll)
        tot += 1; ok += (width == len(inter) == formula and len(imI) * len(imC) % len(imAll) == 0)
    print(f"T5(a) linear codes: {tot} random parity-check maps over Z/2, Z/3: width = |im_I meet im_Ic| = |im_I||im_Ic|/|im psi| in {ok} of {tot}")

# ------------------------------------------------------------------ Theorem 4(d): simulation of the two-list model
def t4d():
    delta = 1 / 4000.0; trials = 4000
    for q in (20, 60, 120):
        hit = 0
        for _ in range(trials):
            a = [rnd.random() for _ in range(q // 2)]; c = sorted(rnd.random() for _ in range(q // 2))
            found = False
            for v in a:                                 # exact: any c with frac(v + c) < delta
                for w in c:
                    if (v + w) % 1.0 < delta: found = True; break
                if found: break
            hit += found
        print(f"T4(d) q={q}, delta=1/4000: P(feasible pair among queried) = {hit / trials:.4f} <= q^2 delta/4 = {q * q * delta / 4:.4f}")

if __name__ == "__main__":
    which = sys.argv[1:] or ["t1", "t3", "t4a", "t4c_counter", "t5a", "t4d", "t4bc"]
    for w in which: globals()[w]()

# verifier: adversarial small-instance tests of the statements of Theorems 1, 2, 3, 4
import random, math, heapq, itertools
from fractions import Fraction
from math import prod, gcd
random.seed(20261126)
PR = [2, 3, 5, 7, 11, 13, 17, 19, 23]
def crt(res, mods):
    P = prod(mods); return sum(x * pow(P // r, -1, r) * (P // r) for x, r in zip(res, mods)) % P
# ---------- Theorem 1(b)
fails = 0; maxratio = 0
for it in range(400):
    m = random.randint(1, 5); mods = [random.choice([2, 3, 4, 5, 6]) for _ in range(m)]
    tabs = [sorted(random.randint(0, 6) for _ in range(r)) for r in mods]
    order = sorted(range(m), key=lambda t: tabs[t][1] - tabs[t][0]); tabs = [tabs[t] for t in order]; mods = [mods[t] for t in order]
    sc = lambda x: sum(tabs[t][x[t]] for t in range(m))
    root = tuple([0] * m); heap = [(sc(root), root)]; out = []; pushes = 1; seen = {root}
    total = prod(mods)
    while heap:
        s, x = heapq.heappop(heap); out.append((s, x))
        nz = [t for t in range(m) if x[t]]
        ch = []
        if not nz: ch.append(tuple([1] + [0] * (m - 1)))
        else:
            t = nz[-1]; p = x[t]
            if p + 1 < mods[t]: y = list(x); y[t] = p + 1; ch.append(tuple(y))
            if t + 1 < m:
                y = list(x); y[t + 1] = 1; ch.append(tuple(y))
                if p == 1: y = list(x); y[t] = 0; y[t + 1] = 1; ch.append(tuple(y))
        for y in ch:
            if y in seen: fails += 1
            seen.add(y); assert sc(y) >= s; heapq.heappush(heap, (sc(y), y)); pushes += 1
    if len(out) != total or [s for s, _ in out] != sorted(sc(x) for x in itertools.product(*[range(r) for r in mods])): fails += 1
    maxratio = max(maxratio, pushes / len(out))
print("Theorem 1(b): 400 instances, failures", fails, "; pushes per output at most", round(maxratio, 2), "(every point is pushed once, so <= 1 overall; <= 3 per pop)")
# ---------- Theorem 2 and 3(i), random instances, exhaustive over G
bad2 = bad3a = bad3b = 0; npts = 0; worst = 0
for it in range(300):
    m = random.randint(2, 5); mods = random.sample(PR, m); P = prod(mods)
    if P > 40000: continue
    X = random.randint(1, P); B = random.randint(1, 3 * P); 
    u = [pow(P // r, -1, r) for r in mods]
    y = [random.randrange(r) for r in mods]; ny = crt(y, mods)
    E = random.randint(1, m)
    lo = Fraction(-B * ny, P) - E; hi = Fraction(B * (X - ny), P)
    T = {n % B for n in range(math.floor(lo) + 1, math.ceil(hi))}
    for x in range(P):
        xs = [x % r for r in mods]
        if sum(Fraction(xi * ui, r) for xi, ui, r in zip(xs, u, mods)) % 1 != Fraction(x, P): bad2 += 1
        off = sum(1 for xi, yi in zip(xs, y) if xi != yi)
        if off > E: continue
        npts += 1
        srho = sum((B * (((xi - yi) * ui) % r)) // r for xi, yi, ui, r in zip(xs, y, u, mods)) % B
        inR = srho in T
        if x < X and not inR: bad3a += 1
        if inR:
            f = Fraction(x, P)
            ok = (f < Fraction(X, P) + Fraction(E, B)) or (f - 1 > -Fraction(E, B))
            if not ok: bad3b += 1
print(f"Theorem 2: violations {bad2}; Theorem 3(i): points tested {npts}, x<X not in R: {bad3a}, x in R outside (-E/B, delta+E/B): {bad3b}")
# ---------- Theorem 4(a): width of the exact (deterministic) trellis and the fooling set
def widths(mods, X):
    P = prod(mods); out = []
    for cut in range(1, len(mods)):
        I = mods[:cut]; Ic = mods[cut:]; PI = prod(I); PIc = prod(Ic)
        fut = {}
        for x in range(X):
            fut.setdefault(x % PI, set()).add(x % PIc)
        w = len({frozenset(v) for v in fut.values()})
        out.append((w, min(PI, PIc, X)))
    return out
print("Theorem 4(a) widths (width, min(P_I,P_Ic,X)) for 3,5,7,11,13, X=1000:", widths([3, 5, 7, 11, 13], 1000), " e^D =", 15015 / 1000)
viol = 0; tested = 0
for it in range(200):
    m = random.randint(2, 5); mods = random.sample(PR, m); P = prod(mods)
    if P > 20000: continue
    X = random.randint(1, P // 2) if P >= 2 else 1
    for w, lb in widths(mods, X):
        tested += 1
        if w < lb: viol += 1
    # fooling property, pair by pair, at a random cut
    cut = random.randint(1, m - 1); PI = prod(mods[:cut]); PIc = prod(mods[cut:]); n = min(PI, PIc, X)
    for x in range(min(n, 60)):
        for yv in range(x + 1, min(n, 60)):
            z = crt([x % PI, yv % PIc], [PI, PIc]); z2 = crt([yv % PI, x % PIc], [PI, PIc])
            if z < X and z2 < X: viol += 1
print(f"Theorem 4(a): {tested} cuts, violations (width below the bound, or a fooling pair failing): {viol}")
# what happens without X <= P/2
print("   without X <= P/2 (X = P): widths", widths([3, 5, 7, 11], 1155), "(the bound fails there, as it must: hypothesis needed)")
# ---------- Theorem 4(b),(c): exhaustive over subsets A of G_I (|G_I| <= 15)
worstb = 0; worstc = 0; cfgs = 0
for (I, Ic, X, E0) in [([3, 5], [7, 11], 200, 20), ([3, 5], [7, 11], 300, 60), ([15], [7, 13], 300, 40), ([3, 5], [11, 13], 500, 100), ([7], [5, 11, 3], 300, 30), ([13], [3, 5, 7], 400, 80), ([3, 5], [7, 11, 2], 700, 100), ([11], [3, 5, 7, 2], 600, 150), ([3,5],[2,7,11,13], 5000, 2000), ([13],[2,3,5,7,11], 6000, 1500)]:
    PI = prod(I); PIc = prod(Ic); P = PI * PIc; Lam = X + 2 * E0
    if not (Lam * 2 <= P): print("  skip (2 Lam > P)", I, Ic, X, E0); continue
    okc = (E0 >= 1 and 2 * X + 3 * E0 <= P)
    inR = lambda z: z < X + E0 or z >= P - E0
    rows = []
    for a in range(PI):
        s = 0; st = 0
        for c in range(PIc):
            z = crt([a, c], [PI, PIc])
            if inR(z): s |= 1 << c
            if X - E0 <= z < X: st |= 1 << c
        rows.append((s, st))
    best = 0; bests = 0
    for mask in range(1, 1 << PI):
        C = -1; nA = 0
        for a in range(PI):
            if mask >> a & 1: C &= rows[a][0]; nA += 1
        if C == 0: continue
        C &= (1 << PIc) - 1
        best = max(best, nA * bin(C).count("1"))
        ns = sum(bin(rows[a][1] & C).count("1") for a in range(PI) if mask >> a & 1)
        bests = max(bests, ns)
    bb = Lam * Lam / (4 * P) + Lam / min(PI, PIc) + 1
    bc = (5 * E0 / PIc + 1) * (2 * E0 / PI + 1); bc2 = (5 * E0 / PI + 1) * (2 * E0 / PIc + 1)
    cfgs += 1
    print(f"   P_I={PI} P_Ic={PIc} X={X} E0={E0}: largest rectangle {best} <= {bb:.1f} : {best <= bb};  most strip points in a rectangle {bests} <= {min(bc, bc2):.1f} (min of the two forms): {bests <= min(bc, bc2) if okc else 'hypothesis fails'}")

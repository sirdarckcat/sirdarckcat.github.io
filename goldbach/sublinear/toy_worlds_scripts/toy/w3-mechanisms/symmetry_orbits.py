# Mechanism "symmetry": N invariant under the translations x -> x + w, w in F_p  (N = A(x^p - x)).
# Exact statement checked: N - Q(x+w) = (N - Q)(x+w), so the rows of one orbit have the same factorisation type.
# Measured: the chance that N - Q is reducible for every monic irreducible row Q of degree 2..D,
#   for (g1) random monic N of degree n, (g2) random monic N = c mod (x^p - x) (the same residues at F_p as a symmetric N),
#   (s) N = A(x^p - x), A random monic of degree n/p with second coefficient 0 (then the translation-fixed rows are forced).
#   python3 symmetry_orbits.py p D n trials seed
import itertools, random, sys, math
from flint import fq_default_ctx, fq_default_poly_ctx
p, D, n, trials, seed = (int(v) for v in sys.argv[1:6]); random.seed(seed)
F = fq_default_ctx(p, 1); R = fq_default_poly_ctx(F); x = R.gen()
Lp = x ** p - x
rows = []
for d in range(2, D + 1):
    for c in itertools.product(range(p), repeat=d):
        Q = R(list(c) + [1])
        if Q.is_irreducible(): rows.append(Q)
def key(Q): return tuple(int(str(c)) for c in Q.coeffs())
orb = {}; reps = []; fixed = []
for Q in rows:
    kq = key(Q)
    if kq in orb: continue
    o = [Q]
    for w in range(1, p):
        Qw = Q(x + w)
        if key(Qw) != kq: o.append(Qw)
    if len(o) == 1: fixed.append(Q)
    else: assert len(o) == p
    for Qw in o: orb[key(Qw)] = len(reps)
    reps.append(Q)
free = [Q for Q in reps if key(Q) not in {key(f) for f in fixed}]
print(f"F_{p}: {len(rows)} rows of degree 2..{D}; under x -> x+1: {len(free)} free orbits of size {p}, {len(fixed)} fixed rows (Q = C(x^{p} - x))")
def ftype(f): return tuple(sorted((g.degree(), m) for g, m in f.factor()[1]))
# (i) exact check of the orbit statement and of the forcing of the fixed rows on a few N
m = n // p; assert m * p == n
chk = 0
for _ in range(3):
    A = R([random.randrange(p) for _ in range(m - 1)] + [0, 1])
    N = A(Lp)
    for Q in random.sample(rows, min(len(rows), 60)):
        assert ftype(N - Q) == ftype(N - Q(x + 1)); chk += 1
    for Q in fixed: assert not (N - Q).is_irreducible()
print(f"  orbit statement checked on {chk} (N, row) pairs; fixed rows reducible for the symmetric N with zero second coefficient")
def run(gen, rowset):
    hits = 0; tot = 0
    for _ in range(trials):
        N = gen(); c = sum(1 for Q in rowset if (N - Q).is_irreducible())
        hits += (c == 0); tot += c
    return hits, tot / trials
def g1(): return R([random.randrange(p) for _ in range(n)] + [1])
def g2():
    c0 = random.randrange(p)
    return R([c0]) + Lp * R([random.randrange(p) for _ in range(n - p)] + [1])
def s():
    A = R([random.randrange(p) for _ in range(m - 1)] + [0, 1]); return A(Lp)
for name, gen in (("g1 random monic N", g1), (f"g2 random N = c mod (x^{p}-x)", g2), (f"s  N = A(x^{p}-x), trace-zero second coefficient", s)):
    h, mean = run(gen, rows)
    se = math.sqrt(max(h, 1) * (trials - h) / trials) / max(h, 1)
    print(f"  {name}: deg N = {n}, {trials} trials, all rows reducible in {h} ({h/trials:.4f}), exponent -ln = {-math.log(max(h,1)/trials):.3f} +- {se:.3f}, mean number of irreducible N - Q = {mean:.3f}")

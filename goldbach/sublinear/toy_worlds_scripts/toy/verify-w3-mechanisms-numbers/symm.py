# symmetry: hit rates for three families, own sampling
import sys, random, math
from ffg import FF
p = int(sys.argv[1]); D = int(sys.argv[2]); trials = int(sys.argv[3]); seed = int(sys.argv[4])
rng = random.Random(seed)
K = FF(p); x = K.x; n = p ** (4 if p == 3 else 3)
rows = [Q for d in range(2, D + 1) for Q in K.irreducibles(d)]
keys = {str(Q): i for i, Q in enumerate(rows)}
sh = x + K.one
fixed = sum(1 for Q in rows if Q(sh) == Q)
orb = set()
for Q in rows:
    o = []; R = Q
    for i in range(p):
        o.append(keys[str(R)]); R = R(sh)
    orb.add(frozenset(o))
print(f"F_{p}: rows of degree 2..{D}: {len(rows)}; orbits of size {p}: {sum(1 for o in orb if len(o)==p)}, fixed rows {fixed}; n = {n}")
AS = x ** p - x
def count_irr(N):
    return sum(1 for Q in rows if (N - Q).is_irreducible())
def fam_g1(): return K.rand_monic(n, rng)
def fam_g2():
    # N = c + (x^p - x) * T, T monic of degree n - p
    return K.R([rng.choice(K.els)]) + AS * K.rand_monic(n - p, rng)
def fam_s():
    m = n // p
    c = [rng.choice(K.els) for _ in range(m)] + [K.one]
    c[m - 1] = K.zero          # trace-zero second coefficient (prime field: zero)
    return K.R(c)(AS)
for name, fam in (("g1 random monic", fam_g1), ("g2 random = c mod x^p-x", fam_g2), ("s  A(x^p-x), 2nd coeff 0", fam_s)):
    hits = 0; tot = 0
    for t in range(trials):
        c = count_irr(fam()); tot += c
        if c == 0: hits += 1
    r = hits / trials
    print(f"  {name}: {trials} trials, hits {hits} ({r:.4f}), exponent {-math.log(r):.3f} +- {math.sqrt((1-r)/(r*trials)):.3f}, mean irreducible {tot/trials:.3f}", flush=True)

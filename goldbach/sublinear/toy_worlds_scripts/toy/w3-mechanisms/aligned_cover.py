# Mechanism "aligned classes" (one common polynomial R for every modulus: N = R mod pi for all pi of degree <= J,
# i.e. N = R mod V_J).  A row Q is struck iff R - Q has an irreducible factor of degree <= J.
# Exact statement: if deg R = J + 1 (R monic), every monic row of degree J + 1 is struck except Q = R - c, c in F_q^*.
# Measured over F_3, J = 3 (14 primes, total degree 33), rows = all monic irreducibles of degree <= D:
#   rows left by the best aligned class R of each degree, by random nonzero classes, by a greedy choice of classes.
#   python3 aligned_cover.py p J D
import itertools, random, sys
import numpy as np
from flint import fq_default_ctx, fq_default_poly_ctx
p, J, D = (int(v) for v in sys.argv[1:4]); random.seed(2)
F = fq_default_ctx(p, 1); R = fq_default_poly_ctx(F); x = R.gen()
def irr(d): return [R(list(c) + [1]) for c in itertools.product(range(p), repeat=d) if R(list(c) + [1]).is_irreducible()]
primes = [P for j in range(1, J + 1) for P in irr(j)]
rows = [Q for d in range(1, D + 1) for Q in irr(d)]; rdeg = np.array([Q.degree() for Q in rows])
def idx(f):                                   # residue (a polynomial of degree < deg P) as an integer
    v = 0
    for c in reversed(f.coeffs()): v = v * p + int(str(c))
    return v
resQ = np.array([[idx(Q % P) for P in primes] for Q in rows])        # rows x primes
print(f"F_{p}: {len(primes)} primes of degree <= {J} (total degree {sum(P.degree() for P in primes)}), {len(rows)} rows of degree <= {D}")
# exact statement at degree J + 1
bad = 0
for _ in range(50):
    Rr = R([random.randrange(p) for _ in range(J + 1)] + [1]); rr = np.array([idx(Rr % P) for P in primes])
    alive = np.all(resQ != rr, axis=1)
    surv = [rows[i] for i in np.nonzero(alive & (rdeg == J + 1))[0]]
    if not all((Rr - Q).degree() == 0 for Q in surv): bad += 1
print(f"  deg R = {J+1}: the rows of degree {J+1} left are all of the form R - c: checked for 50 random R, exceptions {bad}")
# best aligned R of each degree
for dR in range(J + 1, D + 3):
    best = None; tot = 0; cnt = 0
    it = itertools.product(range(p), repeat=dR) if p ** dR <= 60000 else (tuple(random.randrange(p) for _ in range(dR)) for _ in range(60000))
    for c in it:
        Rr = R(list(c) + [1]); rr = np.array([idx(Rr % P) for P in primes])
        k = int(np.all(resQ != rr, axis=1).sum()); tot += k; cnt += 1
        if best is None or k < best[0]: best = (k, Rr)
    al = np.all(resQ != np.array([idx(best[1] % P) for P in primes]), axis=1)
    print(f"  aligned, R monic of degree {dR} ({cnt} tried): mean rows left {tot/cnt:.1f}, best {best[0]} (R = {best[1]}); by degree of row: "
          + " ".join(f"{d}:{int((al & (rdeg == d)).sum())}" for d in range(1, D + 1)))
# random nonzero classes
rn = []
for _ in range(2000):
    cl = np.array([random.randrange(1, p ** P.degree()) for P in primes]); rn.append(int(np.all(resQ != cl, axis=1).sum()))
print(f"  random nonzero classes (2000): mean {np.mean(rn):.1f}, sd {np.std(rn):.1f}, min {min(rn)}")
# greedy: primes in increasing degree, each takes the class with most rows still alive; then one pass of improvement
alive = np.ones(len(rows), dtype=bool); cls = []
for j, P in enumerate(primes):
    cnts = np.bincount(resQ[alive, j], minlength=p ** P.degree()); c = int(np.argmax(cnts)); cls.append(c); alive &= resQ[:, j] != c
for _ in range(3):
    for j, P in enumerate(primes):
        others = np.ones(len(rows), dtype=bool)
        for i in range(len(primes)):
            if i != j: others &= resQ[:, i] != cls[i]
        cnts = np.bincount(resQ[others, j], minlength=p ** P.degree()); cls[j] = int(np.argmax(cnts))
alive = np.ones(len(rows), dtype=bool)
for j in range(len(primes)): alive &= resQ[:, j] != cls[j]
print(f"  greedy classes with 3 improvement passes: {int(alive.sum())} rows left; by degree: " + " ".join(f"{d}:{int((alive & (rdeg == d)).sum())}" for d in range(1, D + 1)))

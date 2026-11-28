import itertools, sympy
from flint import nmod_poly, fmpz_poly
for p, degs in [(5, [2,3,4,5]), (13, [2,3])]:
    g = sympy.primitive_root(p)
    lg = {pow(g, i, p): i for i in range(p - 1)}
    for d in degs:
        cl = [0, 0, 0, 0]
        for t in itertools.product(range(p), repeat=d):
            c = list(t) + [1]
            lead, fs = nmod_poly(c, p).factor()
            if len(fs) == 1 and fs[0][1] == 1:
                D = int(fmpz_poly(c).discriminant()) % p
                cl[lg[D] % 4] += 1
        print(f"F_{p} degree {d}: disc in g^i*(4th powers), i=0..3: {cl}  (g = {g})")

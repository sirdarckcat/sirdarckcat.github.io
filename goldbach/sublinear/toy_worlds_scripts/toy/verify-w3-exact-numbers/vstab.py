# affine stabilisers of the optima; root-forcing in the invariant families
from vlib import W
from compare1 import mine
import numpy as np
inst = [(3, n) for n in range(5, 19)] + [(5, n) for n in range(4, 13)] + [(7, n) for n in range(4, 11)] + [(9, n) for n in range(3, 10)]
out = []
for q, n in inst:
    w = W(q); x = w.x; hdr, gh, gh0, dh, dh0, top, lst = mine(q, n); Gmax = max(gh)
    for v, G in top:
        if G < Gmax: break
        N = w.poly(v, n); st = []
        for a in w.els[1:]:
            for b in w.els:
                if (a, b) == (w.els[1], w.els[0]): continue
                if N(a * x + b) == a ** n * N: st.append((w.lab[a], w.lab[b]))
        out.append((q, n, v, G, st))
for q, n, v, G, st in out:
    p = 3 if q == 9 else q
    print(f"({q},{n}) optimum index {v} G={G} p|n={n % p == 0} nontrivial affine stabiliser (a,b labels): {st}")
# linear rows of translation-invariant N: root in F_q?
print("root forcing of linear rows in invariant families:")
for q, n in [(3, 12), (5, 10), (7, 7), (9, 6), (9, 9)]:
    w = W(q); x = w.x
    for sq in ([1] if q != 9 else [1, 2, 3, 6]):
        fam = w.family(n, sq) if q ** (n // w.p) <= 729 else w.family(n, sq)[:729]
        allroot = 0; alld2 = 0; mism = 0
        for N in fam:
            hasroot = [any((N - (x - a))(x0) == 0 for x0 in w.els) for a in w.els]
            red = [not (N - (x - a)).is_irreducible() for a in w.els]
            allroot += all(hasroot); alld2 += all(red)
        print(f"  q={q} n={n} s={sq}: members {len(fam)}; every linear row has a root in F_q (killed by a linear modulus): {allroot}; D>=2: {alld2}")

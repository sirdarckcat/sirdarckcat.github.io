import sys
from flint import nmod_poly
q = int(sys.argv[1])
u = nmod_poly([0, q - 1] + [0] * (q - 2) + [1], q)
def poly(idx, d):
    c = []
    for _ in range(d):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)
def irr(f):
    _, fac = f.factor(); return len(fac) == 1 and fac[0][1] == 1
for d in (2, 3):
    for lam in (1, 2, q - 1):
        tot = ok = 0; pats = {}
        for idx in range(q ** d):
            R = poly(idx, d)
            _, fac = (lam * u - R).factor()
            tot += 1
            key = tuple(sorted(g.degree() for g, e in fac for _ in range(e)))
            pats[key] = pats.get(key, 0) + 1
            if len(fac) == 1 and fac[0][1] == 1: ok += 1
        top = sorted(pats.items(), key=lambda kv: -kv[1])[:5]
        print(f"q={q} d={d} lam={lam}: monic R of degree d with lam*(t^q - t) - R irreducible: {ok} of {tot} ({ok/tot:.3f}; 1/q = {1/q:.3f}); commonest factor patterns: {top}")

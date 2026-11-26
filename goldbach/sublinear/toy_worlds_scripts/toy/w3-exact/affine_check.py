# For the best 50 N (by G) and up to 200 N with D = Dmax of every instance: is N fixed up to the scalar a^n by an affine
# substitution x -> a x + b other than the identity?  (a = 1: translation invariance.)
import glob, re
from gfcommon import World
for fn in sorted(glob.glob("out_*_*.txt"), key=lambda s: tuple(int(t) for t in re.findall(r"\d+", s)[-2:])):
    q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:])
    if n < 6: continue
    W = World(q); x = W.x; top = []; dtop = []
    for line in open(fn):
        t = line.split()
        if t[0] == "TOP" and len(top) < 50: top.append(int(t[1]))
        if t[0] == "DTOP" and len(dtop) < 200: dtop.append(int(t[1]))
    def sym(v):
        N = W.poly(v, n); out = []
        for a in W.el[1:]:
            for b in W.el:
                if a == W.F(1) and b == W.F(0): continue
                if N(a * x + b) == a ** n * N: out.append((str(a), str(b)))
        return out
    st = [sym(v) for v in top]; sd = [sym(v) for v in dtop]
    tr = lambda L: sum(1 for s in L if any(a == "1" for a, b in s)); other = lambda L: sum(1 for s in L if any(a != "1" for a, b in s))
    print(f"q={q} n={n}: best 50 by G: {tr(st)} translation-invariant, {other(st)} fixed by some x -> ax+b with a != 1 (rank of first: {next((i + 1 for i, s in enumerate(st) if s), None)});"
          f" D = Dmax ({len(dtop)} listed): {tr(sd)} translation-invariant, {other(sd)} with a != 1")

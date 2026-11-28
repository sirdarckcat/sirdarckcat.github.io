import itertools
from fam import world, rows_upto, GD, poly
q, n = 9, 6
p, F, R, x, el = world(q)
good = []
for al in el:
    ok = all(not (x**6 + al*x**3 + x**2 + g).is_irreducible() for g in el)
    nirr = sum((x**6 + al*x**3 + x**2 + g).is_irreducible() for g in el)
    good.append((str(al), ok, nirr))
print("alpha: all x^6+alpha x^3+x^2+gamma reducible?, #irreducible gamma:", good)
# top of (9,6) from the independent enumerator
import re
for line in open("enum_mid.txt").read().split("q ")[1:]:
    if line.startswith("9 n 6 "):
        for g, v in re.findall(r"\(G=(\d+) v=(\d+)\)", line)[:5]:
            N = poly(R, F, el, q, int(v), n); cs = N.coeffs()
            print(g, N, "F2:", cs[2] == 1 and cs[4] == 0 and cs[5] == 0)

# The translation-invariant families, computed independently of the C program (python-flint), against the complete
# enumeration.  For a subgroup H = {b*c : b in F_p} of (F_q,+) the invariant monic polynomials of degree n (p | n)
# are the monic polynomials of degree n/p in y_c = x^p - c^(p-1) x.  For each family: G and D of every member,
# and the "root law":  #{N in family : D >= d}  against  |family| * (#{all N : D >= d} / q^n)^(1/|H|).
import sys, re, itertools, collections, math
from gfcommon import World
fn = sys.argv[1]; q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:])
W = World(q); p = W.p; x = W.x; assert n % p == 0
DH = collections.Counter(); GH = collections.Counter(); rb = None
for line in open(fn):
    t = line.split()
    if t[0] == "DH" and int(t[1]) <= n: DH[int(t[2])] += int(t[3])
    if t[0] == "GH" and int(t[1]) <= n: GH[int(t[2])] += int(t[3])
    if t[0] == "rows_below:": rb = [0] + [int(v) for v in t[1:]]
    if t[0] == "Gmax": Gmax = int(t[1]); Dmax = int(t[3])
tot = q ** n
Kd = {d: sum(v for dd, v in DH.items() if dd >= d) for d in range(1, n + 1)}
def A(g): return sum(v for gg, v in GH.items() if gg >= g)
rows = W.rows(min(n - 1, Dmax + 1))
def GD(N):
    for i, Q in enumerate(rows):
        if (N - Q).is_irreducible(): return i, Q.degree()
    return len(rows), n
def family(ys, m):          # monic polynomials of degree m in ys
    for cs in itertools.product(W.el, repeat=m):
        N = ys ** m
        for k, c in enumerate(cs): N = N + c * ys ** k
        yield N
fams = []
if q == p: fams.append(("F_p[x^p - x]", x ** p - x, p))
else:
    seen = set()
    for c in W.el[1:]:
        key = frozenset(str(c * b) for b in (W.F(1), W.F(2)))
        if key in seen: continue
        seen.add(key); fams.append((f"F_9[x^3 - ({c})^2 x]", x ** 3 - c * c * x, 3))
    if n % 9 == 0: fams.append(("F_9[x^9 - x]", x ** 9 - x, 9))
print(f"q={q} n={n}: all N: Gmax={Gmax} Dmax={Dmax}; #D>=d: " + ", ".join(f"{d}:{Kd[d]}" for d in range(2, Dmax + 1)))
for name, ys, h in fams:
    m = n // ys.degree(); res = [(GD(N), N) for N in family(ys, m)]
    size = len(res); best = max(res, key=lambda t: t[0][0]); bestG = best[0][0]
    print(f"  family {name}: {size} members (|H| = {h}); best G = {bestG} (N = {best[1]}), D = {best[0][1]};"
          f" all N with G >= {bestG}: {A(bestG)} of {tot}  => blind search needs q^n/A = {tot / A(bestG):.3g} members for what the family gives in {size}"
          f" ({math.log(tot / A(bestG) / size):.2f} nats)")
    for d in range(2, Dmax + 1):
        F = sum(1 for (g, dd), N in res if dd >= d)
        print(f"      D >= {d}: family {F:>6} ({F / size:.3e})   all {Kd[d] / tot:.3e}   root-law prediction {size * (Kd[d] / tot) ** (1 / h):.2f}"
              f"   enrichment {F / size / (Kd[d] / tot):.3g}")

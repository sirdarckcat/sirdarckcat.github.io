# The reflection family (works for every n): N(x0 + t) = (-1)^n N(x0 - t), i.e. N = F((x-x0)^2) (n even) or (x-x0) F((x-x0)^2) (n odd).
# For such N the rows Q of degree d = n (mod 2) are permuted by Q(x) -> (-1)^n Q(2 x0 - x) and N - Q keeps its factorisation type,
# so the hits in those degrees come in pairs (the proof is the orbit lemma with the affine map x -> 2 x0 - x).
# Exact counts against the complete enumeration.
import sys, re, itertools, collections
from gfcommon import World
fn = sys.argv[1]; q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:]); W = World(q); x = W.x
DH = collections.Counter(); rb = None
for line in open(fn):
    t = line.split()
    if t[0] == "DH" and int(t[1]) <= n: DH[int(t[2])] += int(t[3])
    if t[0] == "Gmax": Gmax = int(t[1]); Dmax = int(t[3])
tot = q ** n; rows = W.rows(min(n - 1, Dmax + 1)); fam = {}
for x0 in W.el:
    u = (x - x0) ** 2; m = n // 2
    for cs in itertools.product(W.el, repeat=m):
        N = u ** m
        for k, c in enumerate(cs): N = N + c * u ** k
        if n % 2: N = N * (x - x0)
        fam[str(N)] = N
res = []
for N in fam.values():
    g = next((i for i, Q in enumerate(rows) if (N - Q).is_irreducible()), len(rows)); res.append((rows[g].degree() if g < len(rows) else n, g))
print(f"q={q} n={n}: reflection family {len(fam)} members of {tot}; best G in family {max(g for d, g in res)} (all N: {Gmax})")
for d in range(2, Dmax + 1):
    F = sum(1 for dd, g in res if dd >= d); K = sum(v for dd, v in DH.items() if dd >= d)
    print(f"    D >= {d}: family {F:>6} ({F / len(fam):.3e})   all {K:>10} ({K / tot:.3e})   enrichment {F / len(fam) / (K / tot):8.2f}")

# families of translation-invariant N inside the complete enumerations: my own generator + my own G tables
import numpy as np, os, collections
from vlib import W
from compare1 import mine
def rowsbelow(q, n):
    for line in open(f"out/v_{q}_{n}.txt"):
        if line.startswith("rows_below"): return [int(x) for x in line.split()[1:]]
def Dof(G, rb, n):
    # rb[d-1] = rows of degree < d ; D = degree of row G
    for d in range(1, n):
        if G < rb[d]: return d
    return n
ratios = []
for q, n in [(3,6),(3,9),(3,12),(3,15),(3,18),(5,5),(5,10),(7,7),(9,3),(9,6),(9,9)]:
    w = W(q); rb = rowsbelow(q, n); hdr, gh, gh0, dh, dh0, top, lst = mine(q, n)
    Dmax = max(dh); Gmax = max(gh); cumD = {d: sum(c for dd, c in dh.items() if dd >= d) for d in range(2, Dmax + 1)}
    sqs = [1] if q != 9 else [1, 2, 3, 6]; h = w.p
    fn = f"out/v_{q}_{n}.g16"; g = np.fromfile(fn, dtype=np.uint16) if os.path.exists(fn) else None
    totD = 0; best = []
    for sq in sqs:
        if g is not None:
            fam = w.family(n, sq); idx = [w.index(N) for N in fam]; Gs = [int(g[i]) for i in idx]
        else:
            ent = [(v, G) for tag, v, G, D in lst if tag == f"fam{sq}"]; idx = [v for v, G in ent]; Gs = [G for v, G in ent]
        Ds = [Dof(G, rb, n) for G in Gs]
        obs = [sum(1 for D in Ds if D >= d) for d in range(2, Dmax + 1)]
        pred = [cumD[d] ** (1.0 / h) for d in range(2, Dmax + 1)]
        nD = sum(1 for D in Ds if D == Dmax); totD += nD
        bg = max(Gs); rank = sum(c for gg, c in gh.items() if gg > bg) + 1
        print(f"q={q} n={n} s={sq}: members {len(Gs)}; D>=d (d=2..{Dmax}) observed {obs} predicted {[round(x, 2) for x in pred]}; #D=Dmax {nD} of {dh[Dmax]}; best G {bg} (Gmax {Gmax}; rank {rank}); optimum in family: {bg == Gmax}; enrichment at Dmax {(nD / len(Gs)) / (dh[Dmax] / q ** n):.4g}")
        if q != 9: ratios += [o / pr for o, pr in zip(obs, pred)]
        else: print("    ratios", [round(o / pr, 2) for o, pr in zip(obs, pred)])
    if q == 9: print(f"   q=9 n={n}: union over the 4 subgroups: #D=Dmax {totD} of {dh[Dmax]}")
print("prime q: ratio observed/predicted min %.3f max %.3f" % (min(ratios), max(ratios)))
ratios2 = [r for r in ratios]

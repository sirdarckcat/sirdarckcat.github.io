# families beyond enumeration, my own flint code. usage: vbig.py q n maxrowdeg [nsample]
import sys, random, time
from vlib import W
q, n, md = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); ns = int(sys.argv[4]) if len(sys.argv) > 4 else 0
w = W(q); t0 = time.time()
rows = []; rb = {1: 0}
for d in range(1, md + 1):
    for v, P in w.irreducibles(d): rows.append((d, P))
    rb[d + 1] = len(rows)
def GD(N):
    for i, (d, Q) in enumerate(rows):
        if (N - Q).is_irreducible(): return i, d
    return len(rows), md + 1
fam = w.family(n, 1); res = [GD(N) for N in fam]
cnt = {d: sum(1 for G, D in res if D >= d) for d in range(2, md + 2)}
print(f"q={q} n={n}: family {len(fam)} members; rows of degree<=d: {rb}; #D>=d: {cnt}  ({time.time()-t0:.0f}s)")
bestG = max(G for G, D in res); print("  best G", bestG, "attained by", [str(N) for N, (G, D) in zip(fam, res) if G == bestG][:3], "(G capped at", len(rows), ")")
if ns:
    random.seed(987654321); c = {d: 0 for d in range(2, md + 2)}
    for _ in range(ns):
        N = w.poly(random.randrange(q ** n), n); G, D = GD(N)
        for d in c:
            if D >= d: c[d] += 1
    print(f"  random sample {ns}: #D>=d {c}; root-law prediction |fam|*(rate)^(1/p):", {d: round(len(fam) * (c[d] / ns) ** (1.0 / w.p), 1) for d in c if c[d]}, f"({time.time()-t0:.0f}s)")

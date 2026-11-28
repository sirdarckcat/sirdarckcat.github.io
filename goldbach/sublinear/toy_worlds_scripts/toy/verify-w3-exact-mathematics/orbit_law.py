# L4 with orbit counts instead of R/h (q = 3): block pass rates from the complete enumeration (my enum output), family counts from fam.py output above
import re
from fam import world, rows_upto
p, F, R, x, el = world(3)
rows = rows_upto(R, F, el, 3, 7)
I = {}; fixed = {}
for Q in rows:
    d = Q.degree(); I[d] = I.get(d, 0) + 1; fixed[d] = fixed.get(d, 0) + (Q.compose(x + 1) == Q)
orb = {d: (I[d] - fixed[d]) // 3 + fixed[d] for d in I}
print("degree: rows, translation-fixed rows, orbits:", {d: (I[d], fixed[d], orb[d]) for d in I})
K = {}
for fn in ("enum_small.txt", "enum_mid.txt", "enum_big.txt"):
    L = open(fn).read().split("\n")
    for i, s in enumerate(L):
        m = re.match(r"q 3 n (\d+) ", s)
        if m: K[int(m.group(1))] = {int(a): int(b) for a, b in re.findall(r"(\d+):(\d+)", L[i + 2])}
fam = {9: [27, 24, 13, 9, 4, 1], 12: [81, 70, 45, 39, 16, 3], 15: [243, 222, 153, 119, 70, 21], 18: [729, 677, 489, 383, 228, 72, 7]}
for n in (9, 12, 15, 18):
    tot = 3 ** n; size = 3 ** (n // 3); prev = tot; pr_root = 1.0; pr_orb = 1.0; out = []
    for j, d in enumerate(range(2, 2 + len(fam[n]))):
        blk = K[n][d] / prev; prev = K[n][d]; dd = d - 1
        pr_root *= blk ** (1 / 3); pr_orb *= blk ** (orb[dd] / I[dd])
        out.append(f"d={d}: obs {fam[n][j]} root {size * pr_root:.1f} ({fam[n][j] / (size * pr_root):.2f}) orbit {size * pr_orb:.1f} ({fam[n][j] / (size * pr_orb):.2f})")
    print(f"(3,{n}): " + "; ".join(out))

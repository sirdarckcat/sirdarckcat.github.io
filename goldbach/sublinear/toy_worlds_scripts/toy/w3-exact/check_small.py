# Independent check of gfgold.c on small instances: recompute G(N), D(N) for every monic N with python-flint
# (irreducibility by flint, no sieve) and compare with the histogram and the list written by the C program.
import sys, collections
from gfcommon import World
q, n = int(sys.argv[1]), int(sys.argv[2]); fn = sys.argv[3]
W = World(q); rows = W.rows(n - 1)
GH = collections.Counter(); DH = collections.Counter(); top = {}
for v in range(q ** n):
    N = W.poly(v, n); G = len(rows); D = n
    for i, Q in enumerate(rows):
        if (N - Q).is_irreducible(): G = i; D = Q.degree(); break
    GH[G] += 1; DH[D] += 1; top[v] = G
cGH = collections.Counter(); cDH = collections.Counter(); ctop = {}
for line in open(fn):
    t = line.split()
    if t[0] == "GH" and int(t[1]) <= n: cGH[int(t[2])] += int(t[3])
    if t[0] == "DH" and int(t[1]) <= n: cDH[int(t[2])] += int(t[3])
    if t[0] == "TOP": ctop[int(t[1])] = int(t[2])
print(f"q={q} n={n}: rows {len(rows)}; G histogram equal: {GH == cGH}; D histogram equal: {DH == cDH}; "
      f"TOP list ({len(ctop)} entries) equal: {all(top[v] == g for v, g in ctop.items())}; max G {max(GH)}, max D {max(DH)}")

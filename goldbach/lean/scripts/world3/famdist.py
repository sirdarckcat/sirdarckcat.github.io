import sys
from flint import nmod_poly
q, n, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
m = n // q
def poly(idx, dd):
    c = []
    for _ in range(dd):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)
def index(f):
    c = [int(x) for x in f.coeffs()]
    return sum(c[i] * q ** i for i in range(len(c) - 1))
shift = nmod_poly([1, 1], q)
reps = []; seen = set()
for idx in range(q ** d):
    if idx in seen: continue
    f = poly(idx, d); _, fac = f.factor()
    if not (len(fac) == 1 and fac[0][1] == 1): continue
    reps.append(f); g = f
    for _ in range(q):
        seen.add(index(g)); g = g(shift)
u = nmod_poly([0, q - 1] + [0] * (q - 2) + [1], q)
res = []
for x in range(q ** m):
    N = poly(x, m)(u)
    succ = left3 = 0
    for Q in reps:
        _, fac = (N - Q).factor()
        if len(fac) == 1 and fac[0][1] == 1: succ += 1
        if min(f.degree() for f, e in fac) > 3: left3 += 1
    res.append((succ, left3, x))
print(f"q={q} n={n}: {len(reps)} orbits of rows of degree {d}; family {q**m}")
h = {}
for s, l, x in res: h[s] = h.get(s, 0) + 1
print('successful orbits: members ->', sorted(h.items())[:25])
res.sort()
print('fewest successes (successes, orbits left after degree 3, g index):', res[:12])
import statistics
print('mean successes %.2f, mean orbits left after degree 3: %.1f' % (statistics.mean(s for s, l, x in res), statistics.mean(l for s, l, x in res)))
# relation between cover and successes
bins = {}
for s, l, x in res: bins.setdefault(l // 5 * 5, []).append(s)
print('orbits left (bin of 5): members, mean successes ->', [(k, len(v), round(statistics.mean(v), 2)) for k, v in sorted(bins.items())])

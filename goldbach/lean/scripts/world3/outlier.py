import sys
from flint import nmod_poly
q, n, gidx, dmax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
m = n // q
def poly(idx, d):
    c = []
    for _ in range(d):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)
u = nmod_poly([0, q - 1] + [0] * (q - 2) + [1], q)
g = poly(gidx, m); N = g(u)
print('g =', g, '| N =', N)
print("N' =", N.derivative(), "| g' =", g.derivative())
for d in range(1, dmax + 1):
    tot = irr = odd = nsq = 0; pat = {}
    for idx in range(q ** d):
        Q = poly(idx, d)
        _, fq = Q.factor()
        if not (len(fq) == 1 and fq[0][1] == 1): continue
        tot += 1
        _, fac = (N - Q).factor()
        om = sum(e for _, e in fac); sq = all(e == 1 for _, e in fac)
        if len(fac) == 1 and fac[0][1] == 1: irr += 1
        if not sq: nsq += 1
        elif om % 2 == 1: odd += 1
        key = tuple(sorted(f.degree() for f, e in fac for _ in range(e)))
        if d >= dmax - 1: pat[key] = pat.get(key, 0) + 1
    print(f"degree {d}: rows {tot}, irreducible N-Q {irr}, squarefree with odd number of factors {odd}, not squarefree {nsq}")
    if d >= dmax - 1:
        print('   commonest factor patterns:', sorted(pat.items(), key=lambda kv: -kv[1])[:6])

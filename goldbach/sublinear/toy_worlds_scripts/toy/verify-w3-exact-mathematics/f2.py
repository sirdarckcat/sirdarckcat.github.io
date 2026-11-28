import itertools, collections
from fam import world, rows_upto, GD
q, n = 9, 6
p, F, R, x, el = world(q)
rows = rows_upto(R, F, el, q, 3)
lin = [Q for Q in rows if Q.degree() == 1]; quad = [Q for Q in rows if Q.degree() == 2]
print(len(lin), len(quad))
def chi(a): return 0 if a == 0 else (1 if a.is_square() else -1)
tot = 0; d3 = 0; allquad = 0; bytype = collections.Counter(); byc = collections.Counter(); cubes = collections.Counter()
oddlin = collections.Counter(); best = (0, None)
for a, b, c in itertools.product(el, repeat=3):
    N = x ** 6 + a * x ** 3 + b + x ** 2 + c * x
    tot += 1
    okq = all(not (N - Q).is_irreducible() for Q in quad); allquad += okq
    ncube = sum(1 for Q in quad if (N - Q).derivative().is_zero()); cubes[ncube] += 1
    okl = all(not (N - Q).is_irreducible() for Q in lin)
    # parity of linear rows
    no = 0
    for Q in lin:
        f = N - Q; fac = f.factor()[1]
        sqf = all(m == 1 for g, m in fac); r = sum(m for g, m in fac)
        if sqf and r % 2 == 1: no += 1
    oddlin[no] += 1
    if okl and okq: d3 += 1; byc[str(c)] += 1
    g, d = GD(N, rows, n)
    if g > best[0]: best = (g, N, d)
print("F2 members", tot, "all 36 quadratics reducible", allquad, "D>=3", d3, "by c", dict(byc))
print("cube rows per member", dict(cubes), "odd linear rows per member", dict(oddlin))
print("best G within first 3 degrees", best)

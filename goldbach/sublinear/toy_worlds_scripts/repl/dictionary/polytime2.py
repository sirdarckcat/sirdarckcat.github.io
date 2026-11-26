import flint, random
random.seed(2)
def digs(m, b):
    d = []
    while m: m, r = divmod(m, b); d.append(int(r))
    return d
for b in (3, 100, 10, 5, 7):
    for i in range(300):
        n = random.randrange(10**199, 10**200) | 1
        f = flint.fmpz_poly(digs(n, b))
        c, fac = f.factor()
        if len(fac) > 1 or fac[0][1] > 1:
            small = [(g, e) for g, e in fac if g.degree() < 6]
            print(b, "content", c, [(str(g), e, int(g(b))) for g, e in small], [g.degree() for g, e in fac])

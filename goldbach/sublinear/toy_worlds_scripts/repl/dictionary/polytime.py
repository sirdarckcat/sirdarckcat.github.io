import flint, random, time, gmpy2
random.seed(2)
def digs(m, b):
    d = []
    while m: m, r = divmod(m, b); d.append(int(r))
    return d
for b in (2, 3, 10, 100, 65536):
    t = time.time(); red = 0
    for i in range(20):
        n = random.randrange(10**199, 10**200) | 1
        f = flint.fmpz_poly(digs(n, b))
        c, fac = f.factor()
        if len(fac) > 1 or fac[0][1] > 1: red += 1
    print(b, "deg", f.degree(), "sec/poly", (time.time() - t) / 20, "reducible", red)

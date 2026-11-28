import sympy, math, time
from flint import fmpz
rows_all = list(sympy.primerange(3, 6000))
print("odd primes below 6000:", len(rows_all))
def run(name, N):
    t0 = time.time()
    s = 0; n = 0; npr = 0
    for q in rows_all:
        if math.gcd(N, q) != 1: continue      # rows dividing N: N - q divisible by q trivially
        m = N - q
        fs = fmpz(m).factor()
        om = sum(e for _, e in fs)
        assert math.prod(int(pp)**e for pp, e in fs) == m
        s += (-1) ** om; n += 1
        if om == 1: npr += 1
    print(f"{name}: digits {len(str(N))}, rows {n}, mean lam {s/n:+.4f} (se {1/math.sqrt(n):.4f}), N - q prime for {npr}; {time.time()-t0:.0f}s", flush=True)
P = lambda z: math.prod(sympy.primerange(2, z + 1))
run("primorial(43)^2", P(43) ** 2)
run("primorial(29)^3", P(29) ** 3)
run("primorial(13)^8", P(13) ** 8)

# Converse of Cohn's criterion as a compositeness certificate: n = f_b(b) with f_b the base-b digit polynomial;
# f_b = g h in Z[x] gives n = g(b) h(b).  How often is f_b reducible, and what does the factorisation reveal?
import random, time, flint, gmpy2, sys
from common import setup
rows, cov, N0, M, K = setup()
random.seed(4242)
def digs(m, b):
    d = []
    while m: m, r = divmod(m, b); d.append(int(r))
    return d
BASES = (3, 5, 7, 10, 16, 100, 65536)
def run(label, nums, bases):
    t = time.time()
    for b in bases:
        red = 0; vals = []
        for n in nums:
            d = digs(n, b)
            while d[0] == 0: d = d[1:]                 # strip the monomial factor (n divisible by b)
            f = flint.fmpz_poly(d)
            c, fac = f.factor()
            if len(fac) > 1 or fac[0][1] > 1 or abs(int(c)) > 1:
                red += 1
                v = sorted(abs(int(g(b))) for g, e in fac)
                vals.append((v[0], [g.degree() for g, e in fac]))
        s = sorted(vals)
        print(f"{label} | base {b} | {len(nums)} integers | reducible digit polynomials: {red} | smallest factor values g(b) and degrees: {s[:6]} | largest 'smallest factor value': {max([v for v, _ in s], default=None)}", flush=True)
    print(f"  ({time.time() - t:.0f} s)", flush=True)
nA = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
# (a) real rows of real members of the 200,000 cover
A = []
for _ in range(nA // 50):
    N = N0 + random.randrange(K) * M
    A += [N - q for q in random.sample(rows, 50)]
# (b) control: random odd 200-digit integers (not sieved at all)
B = [random.randrange(10 ** 199, 10 ** 200) | 1 for _ in range(nA)]
run("cover rows N - q (200 digits)", A, BASES)
run("random odd 200-digit integers", B, BASES)
run("cover rows N - q (200 digits)", A[:400], (2,))
run("random odd 200-digit integers", B[:400], (2,))

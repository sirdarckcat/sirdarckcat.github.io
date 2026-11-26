# 200 digits, real cover: (1) dictionary images of the Stickelberger-Swan parity against Fermat primality;
# (2) ties between rows paired by the images of an "automorphism".
import numpy as np, math, random, time, gmpy2, flint, sympy
from gmpy2 import mpz, jacobi
from common import setup
rows, cov, N0, M, K = setup()
z = np.load("ind.npz"); ks = z["ks"]; ind = z["ind"]; assert list(z["rows"]) == rows
nm, nr = ind.shape
print(f"{nm} members of the 200,000 cover, {nr} rows, {ind.size} base-2 Fermat tests, {int(ind.sum())} probable primes ({ind.mean():.5f} a row)")
both = int(((ind.sum(1) > 0) & (ind.sum(1) < nr)).sum())
print(f"members with at least one prime row and one composite row: {both} of {nm}")
random.seed(99)
# ---------- (1) features
P6 = mpz(1)
for p in sympy.primerange(467, 10 ** 6): P6 *= p
pr = [(i, j) for i, j in zip(*np.nonzero(ind))]
random.shuffle(pr); pr = pr[:40000]
comp = []
t = time.time(); tried = 0
while len(comp) < 40000:
    i = random.randrange(nm); j = random.randrange(nr); tried += 1
    if ind[i, j]: continue
    m = N0 + int(ks[i]) * M - rows[j]
    if gmpy2.gcd(m, P6) == 1: comp.append((i, j))
print(f"sample: {len(pr)} probable primes; {len(comp)} composites with no prime factor below 10^6 (kept {len(comp)} of {tried} drawn; {time.time() - t:.0f} s)")
def digs(m, b):
    d = []
    while m: m, r = divmod(m, b); d.append(int(r))
    return d
def dder(d, b):
    v = mpz(0)
    for i in range(len(d) - 1, 0, -1): v = v * b + i * d[i]
    return v
feats = {}
def add(name, cls, v):
    feats.setdefault(name, ([], []))[cls].append(v)
t = time.time()
for cls, lst in ((1, pr), (0, comp)):
    for n_, (i, j) in enumerate(lst):
        N = N0 + int(ks[i]) * M; q = rows[j]; m = N - q
        for b in (10, 100, 65536) + ((2,) if n_ < 8000 else ()):
            d = digs(m, b)
            add(f"J_{b} = (f_b'(b) | m)", cls, jacobi(dder(d, b) % m, m))
        if n_ < 8000:
            f = flint.fmpz_poly(digs(m, 65536)); D = mpz(int(f.discriminant()))
            add("K = (disc f_65536 | m)", cls, jacobi(int(D % m), m))
            add("sign disc f_65536", cls, 1 if D > 0 else -1)
            for p in (3, 7, 11, 13):
                add(f"(disc f_65536 | {p}) [parity of the factors of f mod {p}]", cls, jacobi(int(D % p), p))
            d10 = digs(m, 10)
            for p in (7, 13):
                g = flint.nmod_poly(d10, p)
                add(f"f_10 mod {p} has a root [Hensel pattern]", cls, 1 if g.gcd(flint.nmod_poly([0, 1], p) ** p - flint.nmod_poly([0, 1], p)).degree() > 0 else -1)
        add("(-1 | m)", cls, jacobi(-1, m)); add("(2 | m)", cls, jacobi(2, m)); add("(467 | m)", cls, jacobi(467, m))
print(f"features computed in {time.time() - t:.0f} s")
print("feature | primes: n, share +1 | sieved composites: n, share +1 | z of the difference")
zs = []
for name, (c0, c1) in feats.items():
    a = [v for v in c1 if v]; c = [v for v in c0 if v]
    pa = sum(v == 1 for v in a) / len(a); pc = sum(v == 1 for v in c) / len(c); pp = (pa * len(a) + pc * len(c)) / (len(a) + len(c))
    zz = (pa - pc) / math.sqrt(pp * (1 - pp) * (1 / len(a) + 1 / len(c))); zs.append(zz)
    print(f"{name} | {len(a)}, {pa:.4f} | {len(c)}, {pc:.4f} | {zz:+.2f}")
print(f"{len(zs)} features: max |z| {max(abs(x) for x in zs):.2f}, mean z^2 {sum(x * x for x in zs) / len(zs):.2f} (1.00 = no information)")
# ---------- (2) ties
col = ind.sum(0).astype(float)
idx = {q: j for j, q in enumerate(rows)}
def tie(name, pairs):
    pairs = [(a, b) for a, b in pairs if a in idx and b in idx and a < b]
    pairs = sorted(set(pairs))
    if not pairs: print(f"{name} | no pairs"); return
    O = sum(int((ind[:, idx[a]] & ind[:, idx[b]]).sum()) for a, b in pairs)
    E = sum(col[idx[a]] * col[idx[b]] / nm for a, b in pairs)
    T = sum(min(col[idx[a]], col[idx[b]]) for a, b in pairs)
    print(f"{name} | pairs {len(pairs)} | both prime: observed {O}, independent rows {E:.1f} (z {((O - E) / math.sqrt(E)):+.2f}), tied rows about {T:.0f}")
allp = list(sympy.primerange(3, 200000))
print("pairing | pairs of rows | joint primes")
tie("multiplicative involution swapping consecutive primes (3 5)(7 11)...", [(allp[i], allp[i + 1]) for i in range(0, len(allp) - 1, 2)])
tie("multiplicative involution (5 7)(11 13)...", [(allp[i], allp[i + 1]) for i in range(1, len(allp) - 1, 2)])
def refl(q, b):
    d = digs(q, b); return abs(sum(d[i] * (-b) ** i for i in range(len(d))))
def rev(q, b):
    d = digs(q, b); return sum(d[len(d) - 1 - i] * b ** i for i in range(len(d)))
for b in (10, 3, 7, 100):
    tie(f"x -> -x on base-{b} digit polynomials: q* = |Q(-{b})|", [tuple(sorted((q, refl(q, b)))) for q in rows])
for b in (10, 2, 3):
    tie(f"x -> 1/x (digit reversal) in base {b}", [tuple(sorted((q, rev(q, b)))) for q in rows])
tie("x -> 10 - x... translation: q* = Q(b+1) with base-10 digits read in base 11", [tuple(sorted((q, sum(d * 11 ** i for i, d in enumerate(digs(q, 10)))))) for q in rows])
rr = rows[:]; random.shuffle(rr)
tie("control: random pairing", [tuple(sorted((rr[i], rr[i + 1]))) for i in range(0, len(rr) - 1, 2)])
tie("control: neighbouring rows", [(rows[i], rows[i + 1]) for i in range(0, len(rows) - 1, 2)])

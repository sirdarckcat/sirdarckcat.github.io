import sys, pickle, time, math, random
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr, gmpy2
from gmpy2 import mpz, powmod, gcd
F = cr.S + "q200000_m89.txt"
rows, p = cr.load(F); rows = [int(q) for q in rows if q < 200000]
line = [x for x in open(F) if x.startswith(("COVER", "BEST"))][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
M = mpz(2)
for r, a in cov: M *= r
N0 = mpz(0)
# independent CRT: sum form
Mo = M // 2
x = mpz(0)
for r, a in cov:
    c = Mo // r; x += a * c * gmpy2.invert(c, r)
x %= Mo
N0 = x if x % 2 == 0 else x + Mo
assert all(N0 % r == a for r, a in cov) and N0 % 2 == 0
K = (mpz(10) ** 200 - N0) // M
print("rows", len(rows), "moduli", len(cov), "log10 M %.3f log2 K %.3f" % (math.log10(M), math.log2(K)), "room nats: cover %.1f window %.1f" % (math.log(M), math.log(K)))
# check rows: uncovered primes < 200000
import sympy
unc = [q for q in sympy.primerange(3, 200000) if all(q % r != a for r, a in cov)]
print("uncovered odd primes < 200000 (incl. cover primes not in class):", len(unc), " rows from file:", len(rows), " equal sets:", set(unc) == set(rows))
S = pickle.load(open("/tmp/claude-0/-home-user-sirdarckcat-github-io/9ab28896-d478-5e7c-817b-7f69ce9b4074/scratchpad/work/repl/groups-curves/survivors.pkl", "rb"))
ks = sorted(set(k for k, q, b in S))
print("survivor file:", len(S), "rows,", len(ks), "members, per member %.1f" % (len(S) / len(ks)), "prime frac %.4f" % (sum(b for _, _, b in S) / len(S)), " Mertens prediction survivors %.1f" % (len(rows) * math.log(463) / math.log(1e8)))
# spot check survivors: no factor below 2*10^6 on a sample, and labels
random.seed(3); samp = random.sample(S, 300)
pr = list(sympy.primerange(3, 2 * 10**6))
badf = 0; badl = 0
for k, q, b in samp:
    n = N0 + k * M - q
    if any(n % pp == 0 for pp in pr[:20000]): badf += 1
    if bool(gmpy2.is_prime(n, 10)) != b: badl += 1
print("sample 300: with a factor < 224737:", badf, " label mismatches:", badl)
comp = [N0 + k * M - q for k, q, b in S if not b]; prim = [N0 + k * M - q for k, q, b in S if b]
# timings
def best(f, rep=5):
    return min(f() for _ in range(rep))
def tsep(ns):
    t = time.perf_counter()
    for n in ns: powmod(2, n - 1, n)
    return time.perf_counter() - t
sub = comp[:2000]
tF = best(lambda: tsep(sub)) / len(sub)
t = time.perf_counter()
for n in sub: gmpy2.jacobi(3, n)
tJ0 = (time.perf_counter() - t) / len(sub)
H = mpz(random.getrandbits(650)) | 1
t = time.perf_counter()
for n in sub: gmpy2.jacobi(H, n)
tJ = (time.perf_counter() - t) / len(sub)
print(f"Fermat {tF*1e6:.1f} us; jacobi(3/n) {tJ0*1e9:.0f} ns; jacobi(650-bit/n) {tJ*1e9:.0f} ns = {tJ/tF:.4f} Fermat")
# joint: rows of one member
k0 = ks[0]; mem = [(q, N0 + k0 * M - q) for k, q, b in S if k == k0]; N = N0 + k0 * M
for B in (2, 4, 8, 16, 64, len(mem)):
    grp = mem[:B]
    def joint():
        t = time.perf_counter()
        P = mpz(1)
        for q, n in grp: P *= n
        X = powmod(2, N - 1, P)
        res = [X % n == powmod(2, q, n) for q, n in grp]      # naive remainders (cheap vs the exponentiation)
        return time.perf_counter() - t
    tj = best(joint, 3); ts = best(lambda: tsep([n for q, n in grp]), 3)
    P = mpz(1)
    for q, n in grp: P *= n
    X = powmod(2, N - 1, P)
    assert [X % n == powmod(2, q, n) for q, n in grp] == [powmod(2, n - 1, n) == 1 for q, n in grp]
    print(f"batch {B:4d}: joint/separate = {tj/ts:.2f}")
# P-1, B1 = 460 and 100 on 20000 composites not the first ones
def Eof(B):
    E = mpz(1)
    for s in sympy.primerange(2, B + 1):
        e = 1
        while s ** (e + 1) <= B: e += 1
        E *= s ** e
    return E
bits = comp[0].bit_length()
for B in (100, 460, 2000):
    E = Eof(B); sub = comp[-20000:]
    t = time.perf_counter()
    kills = sum(1 for n in sub if gcd(powmod(2, E, n) - 1, n) > 1)
    dt = (time.perf_counter() - t) / len(sub)
    print(f"P-1 B1={B}: bits(E) {E.bit_length()}, cost by bits {E.bit_length()/bits:.3f}, timed {dt/tF:.3f} Fermat; kills {kills}/{len(sub)} = {kills/len(sub):.5f}; kills per timed unit {kills/len(sub)/(dt/tF):.5f}")

"""(b), (d) A battery of invariants cheaper than a Fermat test, on the real rows that survived the sieve to 10^8
(survivors.pkl, 50,636 rows of 100 members, 3,591 primes).  For each binary feature f: its frequency among the
primes and among the composites, and the z-score of the difference.  If a cheap invariant carried information
about primality, some |z| would be large (4 or more) and would reproduce on the two halves of the sample.
"""
import pickle, math, random, time, gmpy2
from gmpy2 import mpz, powmod, jacobi, isqrt, iroot, popcount
from common import setup
rows, cov, N0, M, K = setup()
S = pickle.load(open("survivors.pkl", "rb"))
random.seed(7); H = mpz(random.getrandbits(650)) | 1; H2 = mpz(random.getrandbits(650)) | 1
def euclid(a, b):
    steps = 0; sq = 0; ones = 0
    while b:
        qt, r = divmod(a, b); steps += 1; sq += int(qt & 1); ones += (qt == 1); a, b = b, r
    return steps, sq, ones
feat = {}
def add(name, v): feat.setdefault(name, []).append(1 if v else 0)
lab = []; half = []
T = {"jacobi": 0.0, "trunc": 0.0, "euclid": 0.0, "fermat": 0.0}
for idx, (k, q, b) in enumerate(S):
    N = N0 + k * M; n = N - q; lab.append(b); half.append(k & 1)
    t = time.perf_counter()
    for a in (-1, 2, 3, 5, 7, 11, 13):
        add(f"jacobi({a}/n)  [character of n mod {4*abs(a)}]", jacobi(a, n) == 1)
    add("jacobi(q/n)  [= +-(N/q): residue of N modulo the row]", jacobi(q, n) == 1)
    add("jacobi(H/n), H a fixed random 650-bit odd number", jacobi(H, n) == 1)
    add("jacobi(H2/n)", jacobi(H2, n) == 1)
    s = isqrt(n)
    add("jacobi(isqrt(n)/n)", jacobi(s, n) == 1)
    add("jacobi(isqrt(2n)/n)", jacobi(isqrt(2 * n), n) == 1)
    add("jacobi(iroot(n,3)/n)", jacobi(iroot(n, 3)[0], n) == 1)
    add("jacobi(k/n), k the member index", jacobi(k, n) == 1)
    add("jacobi((2^663 mod n)-1 / n)", jacobi((mpz(1) << 663) % n - 1, n) == 1)
    T["jacobi"] += time.perf_counter() - t
    add("popcount(n) odd", popcount(n) & 1)
    add("bit 100 of n", (n >> 100) & 1)
    add("n - isqrt(n)^2 odd", (n - s * s) & 1)
    add("n - isqrt(n)^2 < isqrt(n)", (n - s * s) < s)
    add("inverse of 2^64 mod n is odd", gmpy2.invert(mpz(1) << 64, n) & 1)
    t = time.perf_counter()
    st, sq, ones = euclid(n, (mpz(1) << 700) % n)
    T["euclid"] += time.perf_counter() - t
    add("Euclid(n, 2^700 mod n): number of steps odd", st & 1)
    add("Euclid: number of odd quotients odd", sq & 1)
    add("Euclid: number of quotients 1 odd", ones & 1)
    st, sq, ones = euclid(n, s)
    add("Euclid(n, isqrt n): steps odd", st & 1)
    t = time.perf_counter()
    e = n - 1
    y = powmod(2, e >> 331, n)                      # top half of the exponent: half a Fermat test
    T["trunc"] += time.perf_counter() - t
    add("top half of the exponent, y = 2^((n-1)>>331): y odd", y & 1)
    add("  y > n/2", 2 * y > n)
    add("  popcount(y) odd", popcount(y) & 1)
    add("  jacobi(y-1/n)", jacobi(y - 1, n) == 1)
    add("  jacobi(y+1/n)", jacobi(y + 1, n) == 1)
    add("  jacobi(y^2+1/n)", jacobi(y * y + 1, n) == 1)
    y3 = powmod(3, e >> 331, n)
    add("  same with base 3: jacobi(y3-1/n)", jacobi(y3 - 1, n) == 1)
    add("  jacobi(y3-y/n)", jacobi(y3 - y, n) == 1)
    w = powmod(2, e & ((mpz(1) << 331) - 1), n)     # low half of the exponent
    add("low half of the exponent, w = 2^((n-1) mod 2^331): w odd", w & 1)
    add("  jacobi(w-1/n)", jacobi(w - 1, n) == 1)
    add("  w > n/2", 2 * w > n)
    y4 = powmod(2, e >> 83, n)                      # 7/8 of the exponent
    add("7/8 of the exponent: jacobi(y-1/n)", jacobi(y4 - 1, n) == 1)
    add("  7/8: y > n/2", 2 * y4 > n)
    t = time.perf_counter(); powmod(2, e, n); T["fermat"] += time.perf_counter() - t
n1 = sum(lab); n0 = len(lab) - n1
print(f"rows {len(lab)}, primes {n1}, composites {n0}")
print(f"time per row: 15 Jacobi symbols {T['jacobi']/len(lab)*1e6:.1f} us, Euclid by hand {T['euclid']/len(lab)*1e6:.1f} us, half exponentiation {T['trunc']/len(lab)*1e6:.1f} us, Fermat {T['fermat']/len(lab)*1e6:.1f} us")
res = []
for name, v in feat.items():
    a1 = sum(x for x, b in zip(v, lab) if b); a0 = sum(v) - a1
    p1 = a1 / n1; p0 = a0 / n0; p = (a1 + a0) / len(lab)
    z = (p1 - p0) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n0)) if 0 < p < 1 else 0.0
    zz = []
    for hh in (0, 1):
        b1 = sum(x for x, b, h in zip(v, lab, half) if b and h == hh); m1 = sum(1 for b, h in zip(lab, half) if b and h == hh)
        b0 = sum(x for x, b, h in zip(v, lab, half) if not b and h == hh); m0 = sum(1 for b, h in zip(lab, half) if not b and h == hh)
        pp = (b1 + b0) / (m1 + m0)
        zz.append((b1 / m1 - b0 / m0) / math.sqrt(pp * (1 - pp) * (1 / m1 + 1 / m0)) if 0 < pp < 1 else 0.0)
    res.append((abs(z), z, p1, p0, zz, name))
print(f"{'feature':62s}  P(f|prime) P(f|comp)     z    z on the two halves (even k, odd k)")
for az, z, p1, p0, zz, name in sorted(res, reverse=True):
    print(f"{name:62s}  {p1:.4f}    {p0:.4f}  {z:+6.2f}   {zz[0]:+5.2f} {zz[1]:+5.2f}")
zs = [r[1] for r in res]
print(f"\n{len(zs)} features: max |z| = {max(abs(z) for z in zs):.2f}, mean z^2 = {sum(z*z for z in zs)/len(zs):.2f} (1.00 if none carries information)")
print(f"a difference of frequencies of {4*math.sqrt(0.25*(1/n1+1/n0)):.3f} would have given |z| = 4")

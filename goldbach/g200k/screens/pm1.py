"""p-1 as a compositeness screen on real 665-bit survivors (surv.txt): stage 1 base 2 with gcd checkpoints at B1 = 100 ... 30,000,
stage 2 (primes in (B1, B2], one mulmod a prime plus one for the product, prime gaps from a table) for (100, 10^4) and (1000, 10^5).
Cost in Fermat tests: squarings (stage 1: bits of the exponent) or mulmods (stage 2: 2 a prime), over the 664 squarings of a test."""
import sys, math, multiprocessing as mp
import gmpy2
from sympy import primerange
CK = [100, 300, 1000, 3000, 10000, 30000]
PR = list(primerange(2, CK[-1] + 1))
def mult(lo, hi):
    """prod of p^(e_hi(p) - e_lo(p)), p^e <= B"""
    m = gmpy2.mpz(1)
    for p in PR:
        if p > hi: break
        e_hi = int(math.log(hi) / math.log(p) + 1e-9); e_lo = int(math.log(lo) / math.log(p) + 1e-9) if p <= lo else 0
        while p ** (e_hi + 1) <= hi: e_hi += 1
        while e_hi > 0 and p ** e_hi > hi: e_hi -= 1
        if p <= lo:
            while p ** (e_lo + 1) <= lo: e_lo += 1
        m *= gmpy2.mpz(p) ** (e_hi - e_lo)
    return m
MULTS, BITS = [], []
lo, tot = 1, gmpy2.mpz(1)
for b in CK:
    m = mult(lo, b) if lo > 1 else mult(1, b)
    MULTS.append(m); tot *= m; BITS.append(int(tot).bit_length()); lo = b
S2 = [(100, 10 ** 4), (1000, 10 ** 5)]
P2 = {s: list(primerange(s[0] + 1, s[1] + 1)) for s in S2}

def stage2(x, n, primes):
    """gcd(prod over primes q of (x^q - 1), n): x^q by the gaps between consecutive primes"""
    gaps = {}
    xq = gmpy2.powmod(x, primes[0], n)
    acc = (xq - 1) % n
    prev = primes[0]
    for q in primes[1:]:
        d = q - prev
        if d not in gaps: gaps[d] = gmpy2.powmod(x, d, n)
        xq = xq * gaps[d] % n
        acc = acc * (xq - 1) % n
        prev = q
    return gmpy2.gcd(acc, n)

def work(line):
    k, q, prp, n = line.split()
    if prp == "1": return None
    n = gmpy2.mpz(n)
    x = gmpy2.mpz(2); first = None; xs = {}
    for b, m in zip(CK, MULTS):
        x = gmpy2.powmod(x, m, n); xs[b] = x
        g = gmpy2.gcd(x - 1, n)
        if first is None and 1 < g < n: first = b
    s2 = []
    for (b1, b2) in S2:
        g = stage2(xs[b1], n, P2[(b1, b2)])
        s2.append(1 < g < n)
    return first, s2

if __name__ == "__main__":
    lines = open("surv.txt").read().splitlines()
    with mp.Pool(4) as pool:
        res = [r for r in pool.map(work, lines, chunksize=64) if r is not None]
    nc = len(res)
    print(f"{nc} composite survivors (665 bits, no factor below 1e8)")
    print("stage 1, base 2: B1, exponent bits, cost in Fermat tests, killed (cumulative), kill fraction c, c / cost, break-even c needs")
    for i, b in enumerate(CK):
        kill = sum(1 for f, _ in res if f is not None and f <= b)
        cost = BITS[i] / 664
        print(f"  B1 = {b:6d}: {BITS[i]:6d} bits, {cost:7.3f} tests, {kill:5d} killed, c = {kill / nc:.4f}, c/e = {kill / nc / cost:.4f} (break-even 1/0.925 = 1.081)")
    for j, (b1, b2) in enumerate(S2):
        i = CK.index(b1)
        kill = sum(1 for f, s in res if (f is not None and f <= b1) or s[j])
        cost = BITS[i] / 664 + 2 * len(P2[(b1, b2)]) / 664
        print(f"  B1 = {b1}, B2 = {b2}: cost {cost:.3f} tests, {kill} killed, c = {kill / nc:.4f}, c/e = {kill / nc / cost:.4f}")

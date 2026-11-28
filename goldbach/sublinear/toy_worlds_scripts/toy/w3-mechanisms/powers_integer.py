# Integer shadow of the "powers / Carlitz / cyclotomic" mechanism (the analogue of 2^n + c).
# N = c * 2^m: N mod r depends only on m mod ord_r(2); the rows are the odd primes q < 200,000 and a row is struck
# when some odd prime r <= 463 divides N - q (the 89 cover primes).  Rows left (not struck), for
#   (a) N = 2^m, 100 <= m <= 664 (powers of two below 10^200, above 10^30);  (b) N = c * 2^m, c odd <= 99, m as large as fits;
#   (c) random even N below 10^200;  (d) the campaign's cover (classes chosen): 1,502.
# Also: the identity "m = m0 mod L  <=>  2^m = 2^m0 mod (2^L - 1)" priced: ln(2^L - 1) nats for the primes of 2^L - 1.
import sys, math, random
import numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
from sympy import primerange, n_order
rows_cov, p = cr.load(cr.S + "q200000_m89.txt")
PR = np.array([q for q in primerange(3, 200000)], dtype=np.int64)
rs = [r for r in primerange(3, 464)]
print(f"rows: {len(PR)} odd primes below 200,000; sieve primes: {len(rs)} odd primes up to 463; cover on file leaves {int((rows_cov < 200000).sum())} rows below 200,000")
qmod = {r: PR % r for r in rs}
def left(N):
    alive = np.ones(len(PR), dtype=bool)
    for r in rs: alive &= qmod[r] != (N % r)
    return int(alive.sum())
def left_classes(cl):
    alive = np.ones(len(PR), dtype=bool)
    for r in rs: alive &= qmod[r] != cl[r]
    return int(alive.sum())
random.seed(5)
rnd = [left(2 * random.randrange(10 ** 199, 5 * 10 ** 199)) for _ in range(3000)]
print(f"(c) random even N: mean {np.mean(rnd):.1f}, sd {np.std(rnd):.1f}, min {min(rnd)}, max {max(rnd)} over {len(rnd)}")
rnz = [left_classes({r: random.randrange(1, r) for r in rs}) for _ in range(3000)]
print(f"(c') random nonzero class at every r (an even N prime to every r <= 463): mean {np.mean(rnz):.1f}, sd {np.std(rnz):.1f}, min {min(rnz)}, max {max(rnz)} over {len(rnz)}")
a = [(left(2 ** m), m) for m in range(100, 665)]
v = [t[0] for t in a]
print(f"(a) N = 2^m, m = 100..664 (565 numbers): mean {np.mean(v):.1f}, sd {np.std(v):.1f}, min {min(a)[0]} at m = {min(a)[1]}")
b = []
for c in range(1, 100, 2):
    mmax = int((200 * math.log(10) - math.log(c)) / math.log(2))
    for m in range(max(1, mmax - 400), mmax + 1): b.append((left(c * 2 ** m), c, m))
vb = [t[0] for t in b]
print(f"(b) N = c*2^m, c odd <= 99, 401 values of m each ({len(b)} numbers): mean {np.mean(vb):.1f}, sd {np.std(vb):.1f}, min {min(b)[0]} at c = {min(b)[1]}, m = {min(b)[2]}")
srt = sorted(rnz)
print(f"    quantile 1/565 of (c'): about {srt[max(0, len(srt) // 565)]} (the expected best of 565 independent draws); best of the 565 powers of two: {min(a)[0]}")
lam = 0.024287
print(f"    exponents at p = {lam}: cover {lam * 1502:.1f}, mean of 2^m {lam * np.mean(v):.1f}, best 2^m {lam * min(a)[0]:.1f}, mean of (c') {lam * np.mean(rnz):.1f}")
# pricing of the congruence on the exponent
for Lx in (12, 60, 180, 360, 660):
    pr = [r for r in rs if Lx % n_order(2, r) == 0]
    print(f"    L = {Lx}: m mod L pins 2^m modulo the {len(pr)} cover primes r with ord_r(2) | L, product = e^{sum(math.log(r) for r in pr):.1f}; "
          f"the congruence is N = 2^m0 mod (2^L - 1), price ln(2^L - 1) = {Lx * math.log(2):.1f} nats; choices of m0: {Lx} (ln = {math.log(Lx):.1f})")

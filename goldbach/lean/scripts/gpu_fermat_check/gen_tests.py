# Test vectors for the GPU kernel (compiled for the CPU) and for the Lean model.
import json, random, sys
random.seed(20261122)
L = 21; B = 1 << 32; R = 1 << (32 * L)
spec = json.load(open(sys.argv[1]))
N0 = int(spec["N0"]); M = int(spec["M"]); U = spec["residual"]
def is_prp(n): return pow(2, n - 1, n) == 1
tests = []; exp = []
def fermat(cq, Mv, k):
    n = cq + k * Mv
    assert n % 2 == 1 and 1 < n < R and cq < R and Mv < R and 0 <= k < B
    tests.append("fermat %x %x %x" % (cq, Mv, k)); exp.append("fermat %d" % int(is_prp(n)))
# campaign-shaped: n = (N0 - q) + k*M, random k below 2^32, including the ends
found = 0
ks = [0, 1, B - 1, B - 2] + [random.randrange(B) for _ in range(36)]
for k in ks:
    q = random.choice(U); fermat(N0 - q, M, k)
# make sure several probable primes are included
k = 12345
while found < 12:
    k += 1
    for q in U[:40]:
        if is_prp(N0 - q + k * M):
            fermat(N0 - q, M, k); found += 1; break
# small and structured n: top limbs zero, pseudoprimes, powers of two plus one, the largest sizes
for n in [3, 5, 7, 9, 15, 341, 561, 645, 1105, 2047, 4033, 65537, 2**32 - 5, 2**32 + 1, 2**32 + 15, 2**64 - 59, 2**64 + 13,
          2**127 - 1, 2**128 + 51, 2**521 - 1, 2**607 - 1, 2**640 + 2**33 + 1, 2**671 + 2**670 + 1, R - 1, R - 3, R - 2**32 - 1, R - 2**64 + 1]:
    fermat(n, 0, 0)                               # cq = n, M = 0
    if n > 2 ** 40:
        k = random.randrange(1, B); Mv = random.randrange(1, n // k + 1) if n // k >= 1 else 0
        cq = n - k * Mv
        if cq >= 0: fermat(cq, Mv, k)
# mont_sqr and dbl_mod on their own
def ninv_of(n): return (-pow(n, -1, B)) % B
mods = [N0 - U[0] + 777 * M, N0 - U[5] + (B - 1) * M, 2**671 + 2**670 + 1, R - 1, R - 2**64 + 1, 2**64 + 13, 65537, 3, 2**640 + 2**33 + 1]
for n in mods:
    xs = [0, 1, 2, n - 1, n - 2, n // 2, n // 2 + 1] + [random.randrange(n) for _ in range(12)]
    xs += [x for x in [B - 1, B, B + 1, (1 << 64) - 1, n - B, (n - 1) ^ (B - 1)] if 0 <= x < n]
    Rinv = pow(R, -1, n)
    for x in xs:
        tests.append("sqr %x %x %x" % (x, n, ninv_of(n))); exp.append("sqr %0*x" % (8 * L, x * x * Rinv % n))
        tests.append("dbl %x %x 0" % (x, n)); exp.append("dbl %0*x" % (8 * L, 2 * x % n))
open("tests.txt", "w").write("\n".join(tests) + "\n"); open("expected.txt", "w").write("\n".join(exp) + "\n")
print(len(tests), "tests:", sum(t.startswith("fermat") for t in tests), "fermat (", sum(e == "fermat 1" for e in exp), "probable primes),",
      sum(t.startswith("sqr") for t in tests), "sqr,", sum(t.startswith("dbl") for t in tests), "dbl")

"""(a) What batching Fermat tests across rows costs, measured with gmpy2 on the real 200-digit rows.
Separate: powmod(2, n-1, n) for each n = N - q.   Joint: X = 2^(N-1) mod prod(n_q), then a remainder tree, compare with 2^q.
"""
import time, random, math, gmpy2
from gmpy2 import mpz, powmod
from common import setup
rows, cov, N0, M, K = setup()
random.seed(1)
k = random.randrange(K); N = N0 + k * M
ns = [N - q for q in rows]
def best(f, rep=5):
    b = 1e9
    for _ in range(rep):
        t = time.perf_counter(); f(); b = min(b, time.perf_counter() - t)
    return b
sub = ns[:256]
tF = best(lambda: [powmod(2, n - 1, n) for n in sub]) / len(sub)
print(f"N has {N.bit_length()} bits; Fermat test powmod(2,n-1,n): {tF*1e6:.1f} us")
a = [mpz(random.getrandbits(660)) for _ in sub]
tS = best(lambda: [x * x for x in a for _ in range(20)]) / (20 * len(sub))
tM = best(lambda: [(x * x) % n for x, n in zip(a, sub) for _ in range(20)]) / (20 * len(sub))
tJ = best(lambda: [gmpy2.jacobi(x, n) for x, n in zip(a, sub) for _ in range(20)]) / (20 * len(sub))
tG = best(lambda: [gmpy2.gcd(x, n) for x, n in zip(a, sub) for _ in range(20)]) / (20 * len(sub))
print(f"square {tS*1e9:.0f} ns, square+reduce {tM*1e9:.0f} ns, jacobi {tJ*1e9:.0f} ns ({tJ/tF:.4f} Fermat), gcd {tG*1e9:.0f} ns ({tG/tF:.4f} Fermat)")
print(f"Fermat test / (bits * (square+reduce)) = {tF/(N.bit_length()*tM):.2f}  (python call overhead is inside the denominator)")
def remtree(X, mods):
    # product tree then remainder tree
    tree = [list(mods)]
    while len(tree[-1]) > 1:
        l = tree[-1]; tree.append([l[i] * l[i + 1] if i + 1 < len(l) else l[i] for i in range(0, len(l), 2)])
    rem = [X % tree[-1][0]]
    for lev in reversed(tree[:-1]):
        rem = [rem[i // 2] % lev[i] for i in range(len(lev))]
    return rem
print("batch  joint/separate   (joint = one exponentiation modulo the product + remainder tree)   exponentiation-only ratio")
for b in (1, 2, 4, 8, 16, 64, 256, 506):
    grp = ns[:b]; qs = rows[:b]
    P = math.prod(grp)
    def joint():
        X = powmod(2, N - 1, P)
        r = remtree(X, grp)
        return [ri == powmod(2, q, n) for ri, q, n in zip(r, qs, grp)]
    def sep():
        return [powmod(2, n - 1, n) == 1 for n in grp]
    assert joint() == sep()
    tj = best(joint, 3); ts = best(sep, 3); te = best(lambda: powmod(2, N - 1, P), 3)
    print(f"{b:5d}  {tj/ts:6.2f}   {te/ts:6.2f}    separate {ts*1e3:.2f} ms  joint {tj*1e3:.2f} ms")
# shared start: 2^(2^j) is below n for j <= 9, so the first 9 of the 664 squarings need no reduction and are identical for all rows
j = 0
while (1 << (1 << (j + 1))) < ns[0]: j += 1
print(f"squarings shared by all rows before the first reduction: {j} of {ns[0].bit_length()} ({j/ns[0].bit_length():.3%}; they are on short operands, so less in time)")

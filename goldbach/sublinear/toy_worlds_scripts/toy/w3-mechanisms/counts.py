# Row counts for the corollary of Theorem 1 (q = 4^m): members N = (L_J * B)^4, n0 = 4 deg L_J the least degree.
# Forced by the theorem with certainty: every monic irreducible row of odd degree d, J < d <= 2J+1 (rows of degree <= J
# divide N - Q... are struck by divisibility), and every irreducible quadratic.  "luck" = forced rows * rough / n0, the
# expected number of irreducible N' - Q for a random N' = 0 mod L_J of degree n0 (rough = prod over monic irreducible pi
# of degree <= J of (1 - |pi|^-1)^-1).  For comparison the odd-characteristic desert of Result 1 (q an odd square,
# N = lam V_J^p): all rows of degree J+1, n0 = p deg V_J.
from sympy import mobius, divisors
import math
def Nd(q, d): return sum(mobius(e) * q ** (d // e) for e in divisors(d)) // d
def degV(q, j): return sum(i * Nd(q, i) for i in range(1, j + 1))
def degL(q, J): return sum(degV(q, J // m) for m in range(1, J + 1))
print("characteristic 2 (Theorem 1), q a power of 4:")
for q in (4, 16, 64, 256):
    for J in (1, 2, 3):
        n0 = 4 * degL(q, J)
        if n0 > 10 ** 7: continue
        odd = sum(Nd(q, d) for d in range(J + 1, 2 * J + 2) if d % 2 == 1) + (Nd(q, 2) if J < 2 else 0)
        allrows = sum(Nd(q, d) for d in range(1, 2 * J + 2))
        rough = math.prod((1 - q ** (-d)) ** (-Nd(q, d)) for d in range(1, J + 1))
        print(f"  q = {q:3d}, J = {J}: deg L_J = {degL(q, J)}, n0 = {n0}; rows of degree <= {2*J+1}: {allrows}; forced by parity: {odd}"
              f" (+ {sum(Nd(q, d) for d in range(1, J + 1))} of degree <= J struck by divisibility); luck replaced {odd * rough / n0:.1f} nats; forced rows per unit of degree {odd / n0:.2f}")
print("odd characteristic (Result 1), q an odd square, N = lam * V_J^p:")
for q, p in ((9, 3), (25, 5), (49, 7), (81, 3)):
    for J in (1, 2, 3):
        if (J + 1) % p == 0: continue
        n0 = p * degV(q, J)
        if n0 > 10 ** 7: continue
        f = Nd(q, J + 1); rough = math.prod((1 - q ** (-d)) ** (-Nd(q, d)) for d in range(1, J + 1))
        print(f"  q = {q:3d}, J = {J}: n0 = {n0}; forced: all {f} rows of degree {J+1}; luck replaced {f * rough / n0:.1f} nats; forced rows per unit of degree {f / n0:.2f}")

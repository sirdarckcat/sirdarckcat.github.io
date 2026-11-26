# Direct check over Z (the case q = 2) of the congruences modulo 8 that the proof of Theorem 1 establishes:
# F = A~^4 - Q~ (arbitrary integer lifts of A, Q in F_2[x], A monic of degree a, Q monic of degree d < 4a,
# Q squarefree mod 2, Q' = S^2 mod 2 with S | A mod 2).  Then, modulo 8,
#   d odd:                      disc(F) = (1+4a) * (-1)^((d-1)/2) * d * disc(Q~)
#   d = 2 mod 4, q_{d-1} = 1:   disc(F) = (1+4a) * (d-1) * (1 + 4 q_{d-2}) * disc(Q~)
#   d = 0 mod 4, q_{d-1} = 1:   disc(F) = (1+4a) * (1+d) * disc(Q~)                      (n - d >= 4 in the even cases)
import random
from flint import fmpz_poly, nmod_poly
random.seed(9)
def disc(P):                       # discriminant of an integer polynomial via the resultant (leading coefficient 1 here)
    n = P.degree(); r = P.resultant(P.derivative())
    return (-1) ** (n * (n - 1) // 2) * r // P[n]
checked = {"odd": 0, "2mod4": 0, "0mod4": 0}; bad = 0
while min(checked.values()) < 400:
    d = random.randrange(2, 12)
    qb = [random.randrange(2) for _ in range(d)] + [1]
    Q2 = nmod_poly(qb, 2)
    if Q2.gcd(Q2.derivative()).degree() != 0: continue
    if d % 2 == 0 and qb[d - 1] == 0: continue
    der = Q2.derivative(); S2 = nmod_poly([int(der[2 * i]) for i in range(der.degree() // 2 + 1)], 2); assert S2 * S2 == der
    B2 = nmod_poly([random.randrange(2) for _ in range(random.randrange(1, 4))] + [1], 2)
    A2 = S2 * B2; a = A2.degree()
    if 4 * a - d < 4: continue
    # arbitrary lifts: add even numbers to the coefficients (leading coefficients stay 1)
    At = fmpz_poly([int(A2[i]) + 2 * random.randrange(-3, 4) for i in range(a)] + [1])
    Qt = fmpz_poly([qb[i] + 2 * random.randrange(-3, 4) for i in range(d)] + [1])
    Ft = At ** 4 - Qt
    lhs = int(disc(Ft)) % 8; dQ = int(disc(Qt))
    if d % 2 == 1: rhs = (1 + 4 * a) * (-1) ** ((d - 1) // 2) * d * dQ; key = "odd"
    elif d % 4 == 2: rhs = (1 + 4 * a) * (d - 1) * (1 + 4 * qb[d - 2]) * dQ; key = "2mod4"
    else: rhs = (1 + 4 * a) * (1 + d) * dQ; key = "0mod4"
    checked[key] += 1; bad += (lhs != rhs % 8)
print("congruences mod 8 for disc(A~^4 - Q~), random lifts over Z:", checked, "disagreements:", bad)

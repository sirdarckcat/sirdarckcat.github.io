"""I2 over Z through an elliptic curve.  E_n : y^2 + xy = x^3 - 36 n x - n   (j = 1728 + 1/n, Delta = n (1+1728n)^2, c4 = 1+1728n, c6 = -(1+1728n)).
Claim (local root numbers, Rohrlich 1993 Prop. 2 for p >= 5): for n >= 1 coprime to 6, with m = 1 + 1728 n,
   w(E_n) = - (-1)^omega(n) * prod_{p | m, v_p(m) odd} (-1/p) * prod_{p | m, v_p(m) = 2 or 4 mod 6} (-3/p),
and the first product is 1 when m is squarefree (m = 1 mod 4).  So for m squarefree: w(E_n) = -(-1)^omega(n): the parity
of the number of prime factors of n is the sign of the functional equation of L(E_n, s).
Checked against PARI's ellrootno (which factors the discriminant)."""
import sys
sys.path.insert(0, "./pylib")
import cypari2, math
from sympy import factorint, jacobi_symbol
pari = cypari2.Pari(); pari.allocatemem(10**9)
tot = bad = sqf = badsq = 0; cnt = {}
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
for n in range(1, LIM):
    if math.gcd(n, 6) != 1: continue
    E = pari.ellinit([1, 0, 0, -36 * n, -n])
    w = int(pari.ellrootno(E))
    m = 1 + 1728 * n; fm = factorint(m); om = len(factorint(n))
    pred = -(-1) ** om
    for p, v in fm.items():
        if v % 2 == 1: pred *= jacobi_symbol(-1, p)
        elif v % 6 in (2, 4): pred *= jacobi_symbol(-3, p)
    tot += 1; bad += (w != pred)
    if all(v == 1 for v in fm.values()):
        sqf += 1; badsq += (w != -(-1) ** om)
    cnt[(om, w)] = cnt.get((om, w), 0) + 1
print(f"n < {LIM} coprime to 6: {tot} curves; formula with the correction at square factors of m fails {bad} times")
print(f"m = 1+1728n squarefree: {sqf} curves; w(E_n) = -(-1)^omega(n) fails {badsq} times")
print("counts by (omega(n), root number):", sorted(cnt.items()))
# 30-digit check: n prime and n = p*q
import random, sympy
random.seed(5)
for trial in range(6):
    p = sympy.nextprime(random.getrandbits(50)); q = sympy.nextprime(random.getrandbits(50))
    for n, om in ((p, 1), (p * q, 2)):
        E = pari.ellinit([1, 0, 0, -36 * n, -n]); w = int(pari.ellrootno(E))
        fm = factorint(1 + 1728 * n)
        print(f"   n with {len(str(n))} digits, omega = {om}: root number {w:+d}, m squarefree: {all(v == 1 for v in fm.values())}")

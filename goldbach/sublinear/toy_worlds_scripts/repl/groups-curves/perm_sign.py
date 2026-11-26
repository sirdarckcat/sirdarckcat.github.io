"""(d) / I2.  Signs of permutations of Z/n: which are cheap and what they know.
A. linear maps (Zolotarev, Frobenius-Zolotarev): sign of x -> Ax on (Z/n)^r is the Jacobi symbol (det A / n).
B. the power map x -> x^k on Z/n (n odd squarefree, gcd(k, p-1) = 1 for all p | n):
      sign = prod over p | n of (-1)^(((k-1)/2) [p = 1 mod 4]),   so for k = 3 mod 4:   mu(n) = (-1)^((n-1)/2) * sign.
C. the power map on the unit group (Z/n)^*, k = 3 mod 4, gcd(k, phi(n)) = 1: odd iff n = p^e with p = 1 mod 4.
D. Dickson polynomials D_k(x,1) on F_p (gcd(k, p^2-1) = 1): sign tabulated.
"""
import math, random, sympy
from sympy import factorint, jacobi_symbol
def sign(perm):
    n = len(perm); seen = bytearray(n); s = 1
    for i in range(n):
        if not seen[i]:
            j = i; L = 0
            while not seen[j]: seen[j] = 1; j = perm[j]; L += 1
            if L % 2 == 0: s = -s
    return s
# A
random.seed(3); bad = 0; tot = 0
for n in range(3, 120, 2):
    for _ in range(6):
        a, b, c, d = [random.randrange(n) for _ in range(4)]
        det = (a * d - b * c) % n
        if math.gcd(det, n) != 1: continue
        perm = [((a * x + b * y) % n) * n + (c * x + d * y) % n for x in range(n) for y in range(n)]
        tot += 1; bad += sign(perm) != jacobi_symbol(det, n)
print(f"A. sign of x -> Ax on (Z/n)^2 = Jacobi(det A / n): {tot} random A, odd n < 120, failures {bad}")
# B
tot = bad = 0; totk3 = badmu = 0
for n in range(3, 6000, 2):
    f = factorint(n)
    if any(e > 1 for e in f.values()): continue
    for k in (3, 5, 7, 11, 13, 15, 19, 23, 27, 31):
        if any(math.gcd(k, p - 1) != 1 for p in f): continue
        s = sign([pow(x, k, n) for x in range(n)])
        pred = 1
        for p in f:
            if p % 4 == 1 and k % 4 == 3: pred = -pred
        tot += 1; bad += s != pred
        if k % 4 == 3:
            mu = (-1) ** len(f); totk3 += 1; badmu += mu != (-1) ** ((n - 1) // 2) * s
print(f"B. power map on Z/n, odd squarefree n < 6000, ten exponents k: {tot} cases, failures of the formula {bad}")
print(f"   k = 3 mod 4: mu(n) = (-1)^((n-1)/2) sign(x -> x^k): {totk3} cases, failures {badmu}")
# C
tot = bad = 0
for n in range(3, 4000, 2):
    f = factorint(n); phi = 1
    for p, e in f.items(): phi *= p ** (e - 1) * (p - 1)
    units = [x for x in range(n) if math.gcd(x, n) == 1]; idx = {x: i for i, x in enumerate(units)}
    for k in (3, 7, 11, 19, 23):
        if math.gcd(k, phi) != 1: continue
        s = sign([idx[pow(x, k, n)] for x in units])
        pred = -1 if (len(f) == 1 and list(f)[0] % 4 == 1) else 1
        tot += 1; bad += s != pred
print(f"C. power map on (Z/n)^*, odd n < 4000, k = 3 mod 4: {tot} cases; 'odd iff n = p^e, p = 1 mod 4' fails {bad} times")
# D
def dickson(k, x, p):
    a, b = 2, x
    for _ in range(k - 1): a, b = b, (x * b - a) % p
    return b if k >= 1 else 2
tab = {}
for p in sympy.primerange(5, 700):
    for k in (5, 7, 11, 13, 17, 19, 23):
        if math.gcd(k, p * p - 1) != 1: continue
        perm = [dickson(k, x, p) for x in range(p)]
        if len(set(perm)) != p: continue
        tab.setdefault((k % 8, p % 16), set()).add(sign(perm))
print("D. Dickson D_k(x,1) on F_p: sign by (k mod 8, p mod 16):")
for key in sorted(tab): print("   ", key, sorted(tab[key]))

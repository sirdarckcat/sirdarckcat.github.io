# independent check: for odd squarefree n and k = 3 mod 4 with gcd(k, p-1) = 1 for all p | n,
# mu(n) = (-1)^((n-1)/2) * sign of the permutation x -> x^k of Z/n
import math
from sympy import factorint
def sign_of(perm):
    n = len(perm); seen = bytearray(n); s = 1
    for i in range(n):
        if not seen[i]:
            j = i; L = 0
            while not seen[j]: seen[j] = 1; j = perm[j]; L += 1
            if L % 2 == 0: s = -s
    return s
tot = bad = 0
for n in range(3, 4001, 2):
    f = factorint(n)
    if any(e > 1 for e in f.values()): continue
    for k in (3, 7, 11, 19, 23, 31, 43):
        if any(math.gcd(k, p - 1) != 1 for p in f): continue
        perm = [pow(x, k, n) for x in range(n)]
        mu = (-1) ** len(f)
        tot += 1; bad += mu != (-1) ** ((n - 1) // 2) * sign_of(perm)
print(f"sign of the power map: {tot} cases (odd squarefree n < 4000, seven exponents), {bad} failures")

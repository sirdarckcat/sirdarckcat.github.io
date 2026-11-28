#!/usr/bin/env python3
"""An integer counterpart of Pellet-Stickelberger-Swan, checked by brute force.

Claim. n odd squarefree, k odd with gcd(k, p-1) = 1 for every prime p | n (so x -> x^k permutes Z/n). Then
    sign(x -> x^k on Z/n)  = (-1)^( (k-1)/2 * #{p | n : p = 1 mod 4} )
    sign(x -> -x on Z/n)   = (-1/n) = (-1)^#{p | n : p = 3 mod 4}          (Zolotarev)
hence for k = 3 mod 4:      mu(n) = (-1)^omega(n) = sign(x -> -x^k on Z/n).
The permutation acts on n points (not on log n points as Frobenius does on the roots of a polynomial).
"""
import sys, math
from sympy import factorint
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
def sign_of(perm):
    n = len(perm); seen = bytearray(n); cyc = 0
    for i in range(n):
        if not seen[i]:
            cyc += 1; j = i
            while not seen[j]: seen[j] = 1; j = perm[j]
    return -1 if (n - cyc) % 2 else 1
tested = bad1 = bad2 = bad3 = 0; byomega = {}
for n in range(3, LIM, 2):
    f = factorint(n)
    if any(e > 1 for e in f.values()): continue
    for kclass in (3, 1):
        k = kclass if kclass > 1 else 5
        while any(math.gcd(k, p - 1) != 1 for p in f): k += 4
        pw = [pow(x, k, n) for x in range(n)]
        s_pow = sign_of(pw)
        n1 = sum(1 for p in f if p % 4 == 1); n3 = len(f) - n1
        if s_pow != (-1) ** (((k - 1) // 2) * n1): bad1 += 1
        if kclass == 3:
            s_neg = sign_of([(-x) % n for x in range(n)])
            if s_neg != (-1) ** n3: bad2 += 1
            s_tot = sign_of([(-y) % n for y in pw])
            mu = (-1) ** len(f)
            if s_tot != mu: bad3 += 1
            byomega[len(f)] = byomega.get(len(f), 0) + 1
            tested += 1
print(f"odd squarefree n < {LIM}: {tested} tested (by number of prime factors: {dict(sorted(byomega.items()))})")
print(f"failures: power-map sign formula {bad1} (k = 3 and k = 1 mod 4), Zolotarev for -1 {bad2}, mu(n) = sign(x -> -x^k) {bad3}")

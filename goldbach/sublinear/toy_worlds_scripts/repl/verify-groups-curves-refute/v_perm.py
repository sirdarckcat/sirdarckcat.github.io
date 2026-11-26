# independent check: sign of x -> x^k on Z/n and on (Z/n)^*, with k a PRIME > n, k = 3 mod 4 (so gcd(k,p-1)=1 automatically)
import sympy, math, random
from sympy import factorint, nextprime
def sign_of(perm):
    n = len(perm); seen = [False]*n; s = 1
    for i in range(n):
        if not seen[i]:
            j = i; L = 0
            while not seen[j]:
                seen[j] = True; j = perm[j]; L += 1
            if L % 2 == 0: s = -s
    return s
def kfor(n, res):
    k = nextprime(n)
    while k % 4 != res: k = nextprime(k)
    return int(k)
fa = fb = fc = fd = 0; ca = cb = 0
for n in range(3, 2500, 2):
    f = factorint(n)
    k = kfor(n, 3); k1 = kfor(n, 1)
    if all(e == 1 for e in f.values()):
        perm = [pow(x, k, n) for x in range(n)]
        assert sorted(perm) == list(range(n))
        s = sign_of(perm)
        mu = (-1) ** len(f)
        if mu != (-1) ** ((n - 1) // 2) * s: fa += 1
        s1 = sign_of([pow(x, k1, n) for x in range(n)])
        if s1 != 1: fb += 1       # k = 1 mod 4: formula gives +1 always
        ca += 1
    # unit group
    U = [x for x in range(n) if math.gcd(x, n) == 1]; idx = {x: i for i, x in enumerate(U)}
    s = sign_of([idx[pow(x, k, n)] for x in U])
    pred = -1 if (len(f) == 1 and list(f)[0] % 4 == 1) else 1
    if s != pred: fc += 1
    # Duke-Hopkins form: sign = (-1)^(r (k-1)/2), r = (phi - #{x: x^2=1})/2
    inv = sum(1 for x in U if x * x % n == 1); r = (len(U) - inv) // 2
    if s != (-1) ** (r * ((k - 1) // 2)): fd += 1
    cb += 1
print(f"Z/n squarefree odd n<2500, k prime>n, k=3 mod 4: {ca} cases, failures of mu(n)=(-1)^((n-1)/2) sgn: {fa}; k=1 mod 4 sign always +1 fails: {fb}")
print(f"(Z/n)^*, odd n<2500 (all, incl. prime powers): {cb} cases, failures 'odd iff p^e, p=1 mod 4': {fc}; failures of Duke-Hopkins form (-1)^(r(k-1)/2): {fd}")

#!/usr/bin/env python3
"""Check of the genus-theory statements used in the I2 obstruction, by brute force on class groups.

n squarefree, n = 1 mod 4, D = -4n.  For every reduced primitive form f of discriminant D:
  (i)   f is a square in Cl(D)  <=>  an integer m represented by f, coprime to 2n, is a square modulo n
        (i.e. modulo every prime factor: the quadratic residuosity problem), and
  (ii)  [Cl : Cl^2] = 2^omega(n), so the 2-rank is omega(n);
  (iii) the Jacobi symbol (m | n) -- the one genus character computable without the factors -- need not be +1 alone,
        but (m|n) * (-1)^((m-1)/2) = +1 on every represented m (the product relation), so it separates nothing.
"""
import math, sys
from sympy import factorint, jacobi_symbol
def reduce(a, b, c):
    while True:
        if c < a: a, b, c = c, -b, a; continue
        if b > a or b <= -a:
            k = (b + a - 1) // (2 * a) if b > a else -((-b + a) // (2 * a))
            k = round((b) / (2 * a)); 
            if b - 2 * k * a > a: k += 1
            if b - 2 * k * a <= -a: k -= 1
            c = a * k * k - b * k + c; b = b - 2 * a * k
            continue
        if a == c and b < 0: b = -b
        return (a, b, c)
def xgcd(a, b):
    if b == 0: return (abs(a), (1 if a >= 0 else -1), 0)
    g, x, y = xgcd(b, a % b); return (g, y, x - (a // b) * y)
def compose(f1, f2, D):
    a1, b1, c1 = f1; a2, b2, c2 = f2
    s = (b1 + b2) // 2
    g, u, v = xgcd(a1, a2); d, x, w = xgcd(g, s)      # d = u' a1 + v' a2 + w s
    u, v = u * x, v * x
    a3 = a1 * a2 // (d * d)
    b3 = (b2 + 2 * (a2 // d) * ((v * (s - b2) - w * c2) % (a1 // d if a1 // d else 1))) if a1 // d else b2
    b3 %= 2 * a3
    c3 = (b3 * b3 - D) // (4 * a3)
    return reduce(a3, b3, c3)
def forms(D):
    out = []; a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a) == 0:
                c = (b * b - D) // (4 * a)
                if c >= a and math.gcd(math.gcd(a, abs(b)), c) == 1 and not (a == c and b < 0): out.append((a, b, c))
        a += 1
    return out
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
tot = bad_i = bad_ii = bad_iii = nforms = 0
for n in range(5, LIM, 4):
    fac = factorint(n)
    if any(e > 1 for e in fac.values()): continue
    D = -4 * n; F = forms(D); S = {compose(f, f, D) for f in F}
    for f in F: assert (f[1] ** 2 - 4 * f[0] * f[2]) == D
    if len(F) != len(S) * 2 ** len(fac): bad_ii += 1
    for (a, b, c) in F:
        m = None
        for x in range(0, 40):
            for y in range(-40, 40):
                v = a * x * x + b * x * y + c * y * y
                if v > 1 and math.gcd(v, 2 * n) == 1 and math.gcd(x, y) == 1: m = v; break
            if m: break
        if m is None: continue
        qr = all(pow(m, (p - 1) // 2, p) == 1 for p in fac)
        if qr != ((a, b, c) in S): bad_i += 1
        if jacobi_symbol(m % n, n) * (1 if m % 4 == 1 else -1) != 1: bad_iii += 1
        nforms += 1
    tot += 1
print(f"squarefree n = 1 mod 4 below {LIM}: {tot} discriminants, {nforms} classes checked")
print(f"failures: (i) square class <=> represented m is a QR mod n: {bad_i};  (ii) [Cl:Cl^2] = 2^omega(n): {bad_ii};  (iii) product relation: {bad_iii}")

# Test of the general parity formula (all rows, including p | deg Q) over prime fields F_p.
#   N of degree n, leading coefficient lam, N' = 0;  Q monic irreducible of degree d < n, Q' != 0,
#   e = deg Q', l = leading coefficient of Q', every root of Q' a root of N.  Then with r the number of
#   irreducible factors of N - Q:
#     (-1)^(n-r) = chi(-1)^A * chi(lam)^(n-2-e) * chi(l)^(n-d) * (-1)^(d-1),
#     A = n(n-1)/2 + n + n e + e + e d + d(d-1)/2.
# For p not dividing d: e = d - 1, l = d and this is the research session's formula.
#   usage: python3 -I gen_parity.py [p:J,p:J,...]     (default 3:1,3:2,5:1,7:1)
import itertools, sys

def trim(a):
    while a and a[-1] == 0: a.pop()
    return a
def add(a, b, p):
    n = max(len(a), len(b)); c = [0] * n
    for i, x in enumerate(a): c[i] = x
    for i, x in enumerate(b): c[i] = (c[i] + x) % p
    return trim(c)
def sub(a, b, p):
    return add(a, [(-x) % p for x in b], p)
def mul(a, b, p):
    if not a or not b: return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                c[i + j] = (c[i + j] + x * y) % p
    return trim(c)
def divmod_(a, b, p):
    a = a[:]; q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], p - 2, p)
    while len(a) >= len(b):
        k = len(a) - len(b); c = a[-1] * inv % p; q[k] = c
        for i, y in enumerate(b): a[i + k] = (a[i + k] - c * y) % p
        trim(a)
    return trim(q), a
def gcd(a, b, p):
    while b: a, b = b, divmod_(a, b, p)[1]
    if a:
        inv = pow(a[-1], p - 2, p); a = [x * inv % p for x in a]
    return a
def powmod(a, e, f, p):
    r = [1]; a = divmod_(a, f, p)[1]
    while e:
        if e & 1: r = divmod_(mul(r, a, p), f, p)[1]
        a = divmod_(mul(a, a, p), f, p)[1]; e >>= 1
    return r
def deriv(a, p):
    return trim([(i * a[i]) % p for i in range(1, len(a))])
def nfactors_squarefree(f, p):
    """number of irreducible factors of a squarefree polynomial (distinct-degree factorisation)"""
    f = f[:]; r = 0; d = 0; xq = [0, 1]
    while len(f) - 1 >= 2 * (d + 1):
        d += 1
        xq = powmod(xq, p, f, p)
        g = gcd(f, sub(xq, [0, 1], p), p)
        if len(g) > 1:
            r += (len(g) - 1) // d
            f = divmod_(f, g, p)[0]
            xq = divmod_(xq, f, p)[1] if len(f) > 1 else [0]
    if len(f) > 1: r += 1
    return r
def is_irreducible(f, p):
    if len(deriv(f, p)) == 0: return False
    if len(gcd(f, deriv(f, p), p)) > 1: return False
    return nfactors_squarefree(f, p) == 1
def monic_irreducibles(d, p):
    for c in itertools.product(range(p), repeat=d):
        f = list(c) + [1]
        if is_irreducible(f, p): yield f
def chi(a, p):
    a %= p
    if a == 0: return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1

CASES = [(int(a), int(b)) for a, b in (x.split(':') for x in sys.argv[1].split(','))] if len(sys.argv) > 1 else [(3, 1), (3, 2), (5, 1), (7, 1)]
bad = 0; total = 0
for (p, J) in CASES:
    if True:
        V = [1]
        for d in range(1, J + 1):
            for f in monic_irreducibles(d, p): V = mul(V, f, p)
        for lam in range(1, p):
            for extra in (0, 1):          # two values of n mod 2: multiply V by x + 0 again
                U = V if extra == 0 else mul(V, [0, 1], p)
                N = [1]
                for _ in range(p): N = mul(N, U, p)
                N = [x * lam % p for x in N]
                n = len(N) - 1
                assert deriv(N, p) == []
                for d in range(2, J + 2):
                    if d >= n: continue
                    stats = {}
                    for Q in monic_irreducibles(d, p):
                        Qp = deriv(Q, p); e = len(Qp) - 1; l = Qp[-1]
                        f = sub(N, Q, p)
                        assert len(gcd(f, deriv(f, p), p)) == 1
                        r = nfactors_squarefree(f, p)
                        A = n * (n - 1) // 2 + n + n * e + e + e * d + d * (d - 1) // 2
                        pred = chi(-1, p) ** A * chi(lam, p) ** (n - 2 - e) * chi(l, p) ** (n - d) * (-1) ** (d - 1)
                        ok = ((-1) ** (n - r) == pred)
                        total += 1; bad += (not ok)
                        key = (e, chi(l, p))
                        stats.setdefault(key, [0, 0, 0])
                        stats[key][0] += 1; stats[key][1] += (r % 2 == 0); stats[key][2] += ok
                    print("p=%d J=%d lam=%d n=%d d=%d%s : %s" % (p, J, lam, n, d, " (p | d)" if d % p == 0 else "",
                          "  ".join("deg Q'=%d chi(lc)=%+d: %d rows, %d with r even, %d agree" % (k[0], k[1], v[0], v[1], v[2]) for k, v in sorted(stats.items()))))
                    sys.stdout.flush()
print("rows tested: %d, disagreements with the formula: %d" % (total, bad))

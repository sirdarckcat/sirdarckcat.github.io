import itertools
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


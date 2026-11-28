import math, random, itertools, sympy
from sympy import jacobi_symbol
# ---- counts table (pure arithmetic) ----
def nirr(q, d):
    return sum(sympy.mobius(d // e) * q**e for e in sympy.divisors(d)) // d
def degV(q, j): return sum(d * nirr(q, d) for d in range(1, j + 1))
def degL(q, J): return sum(degV(q, J // m) for m in range(1, J + 1))
def rough(q, J): return math.prod((1 - q**-d) ** (-nirr(q, d)) for d in range(1, J + 1))
print("char 2: q, J, n0, rows<=2J+1, forced(page convention: odd degrees in (J,2J+1], and degree 2 if J=1), nats; forced incl. degree = 2 mod 4 trace rule up to 2J+1")
def n_trace_rule(q, d):
    # monic irreducibles of even degree d with q_{d-1} != 0 and Tr(q_{d-2}/q_{d-1}^2) = 1 : counted by brute force only for small cases
    return None
for q, J in [(4,1),(4,2),(4,3),(16,1),(16,2),(64,1),(256,1)]:
    n0 = 4 * degL(q, J)
    rows = sum(nirr(q, d) for d in range(1, 2*J + 2))
    forced = sum(nirr(q, d) for d in range(J + 1, 2*J + 2) if d % 2 == 1) + (nirr(q, 2) if J == 1 else 0)
    print(f"  ({q},{J}): deg L_J = {degL(q,J)}, n0 = {n0}, rows = {rows}, forced = {forced}, struck = {sum(nirr(q,d) for d in range(1,J+1))}, nats = {forced*rough(q,J)/n0:.1f}, roughness {rough(q,J):.3f}")
print("odd char: q, J, n0 = p deg V_J, rows of degree J+1, nats")
for q, p, J in [(9,3,1),(25,5,1),(25,5,2),(49,7,2),(81,3,1)]:
    n0 = p * degV(q, J); r = nirr(q, J + 1)
    print(f"  ({q},{J}): n0 = {n0}, rows = {r}, nats = {r*rough(q,J)/n0:.1f}")
print("F_4 J=3 with the 270 degree-6 trace-rule rows added:", (2544+270), "nats", (2544+270)*rough(4,3)/336)
print("model checks: 1480*rough(16,1)/64 =", 1480*rough(16,1)/64, " 236*rough(4,2)/100 =", 236*rough(4,2)/100, " 224*rough(4,2)/100 =", 224*rough(4,2)/100, " 2*48*rough(4,2)/100 =", 2*48*rough(4,2)/100)
# ---- Jacobi(n'|n) ----
rng = random.Random(99)
pr = list(sympy.primerange(3, 400))
exc = 0; joint = {}
for t in range(20000):
    k = rng.randint(1, 6)
    fs = rng.sample(pr, k)
    n = math.prod(fs); nd = sum(n // r for r in fs)
    k3 = sum(1 for r in fs if r % 4 == 3)
    j = jacobi_symbol(nd % n, n)
    if j != (-1) ** (k3 * (k3 - 1) // 2): exc += 1
    joint[(k % 2, j)] = joint.get((k % 2, j), 0) + 1
print("Jacobi(n'|n) = (-1)^C(k3,2): 20000 random odd squarefree n, exceptions", exc, sorted(joint.items()))
# ---- discriminant classes of irreducibles ----
from flint import nmod_poly, fmpz_poly
def disc_mod(coeffs, p):
    return int(fmpz_poly(coeffs).discriminant()) % p
for p, degs in [(5, [2,3,4,5]), (13, [2,3])]:
    g = sympy.primitive_root(p)
    lg = {pow(g, i, p): i for i in range(p - 1)}
    for d in degs:
        cl = [0, 0, 0, 0]
        for t in itertools.product(range(p), repeat=d):
            f = nmod_poly(list(t) + [1], p)
            if f.is_irreducible():
                D = disc_mod(list(t) + [1], p)
                cl[lg[D] % 4] += 1
        print(f"F_{p} degree {d}: disc in g^i*(4th powers), i=0..3: {cl}  (g = {g})")

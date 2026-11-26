#!/usr/bin/env python3
"""Independent test of Theorem A (i),(ii),(iv) on small random instances with ARBITRARY bases (random unimodular
transforms of the triangular basis, plus LLL), moduli not necessarily prime or coprime, including L=1 and L=s."""
import random, math, itertools
from fractions import Fraction
from collections import deque
import flint
random.seed(12345)

def rand_unimodular(n, steps):
    U = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(steps):
        i, j = random.sample(range(n), 2); c = random.choice((-2, -1, 1, 2))
        U[i] = [a + c * b for a, b in zip(U[i], U[j])]
        if random.random() < 0.2: U[i] = [-a for a in U[i]]
    return U

def test(m, maxs, mode):
    sl = [random.randrange(2, maxs) for _ in range(m)]
    lists = []
    for s in sl:
        d = random.choice([d for d in range(1, s + 1) if math.gcd(d, s) == 1]) if s > 1 else 1
        L = random.choice([1, s, random.randrange(1, s + 1), random.randrange(1, s + 1)])
        lists.append((random.randrange(s), d % s if s > 1 else 0, L))
    K = random.randrange(1, 400)
    n = m + 1
    el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]
    ell = [K] + [L for (a, d, L) in lists]
    o = [0] + [e * a for e, (a, d, L) in zip(el, lists)]      # exactly as in the statement (not reduced)
    G = [[0] * n for _ in range(n)]; G[0][0] = 1
    for i, (s, e) in enumerate(zip(sl, el)): G[0][i + 1] = e; G[i + 1][i + 1] = -s
    if mode == "lll":
        A = flint.fmpz_mat(G).lll(); B = [[int(A[i, j]) for j in range(n)] for i in range(n)]
    else:
        U = rand_unimodular(n, random.randrange(0, 6) if mode == "mild" else random.randrange(6, 14))
        B = [[sum(U[i][k] * G[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    assert abs(int(flint.fmpz_mat(B).det())) == math.prod(sl)
    wp = [sum(max(B[i][j], 0) for i in range(n)) for j in range(n)]
    wm = [sum(max(-B[i][j], 0) for i in range(n)) for j in range(n)]
    tau = [Fraction(wp[j] + wm[j], ell[j]) for j in range(n)]
    E = Fraction(K) * math.prod(Fraction(L, s) for s, (a, d, L) in zip(sl, lists))
    # brute force Sol
    Sol = [k for k in range(K) if all(any((a + d * t - k) % s == 0 for t in range(L)) for s, (a, d, L) in zip(sl, lists))]
    low = E * math.prod(max(Fraction(0), 1 - t) for t in tau); up = E * math.prod(1 + t for t in tau)
    assert low <= len(Sol) <= up, ("(i) fails", sl, lists, K, B, float(low), len(Sol), float(up))
    # (iv)
    assert math.prod(tau) * E >= 1, "(iv) fails"
    # (ii) BFS, with a visit cap
    Wb = E * math.prod(1 + 2 * t for t in tau)
    if Wb > 150000: return ("skipped", len(Sol))
    Bq = flint.fmpq_mat(flint.fmpz_mat(B)); y = flint.fmpq_mat([[flint.fmpq(2 * o[j] + ell[j], 2) for j in range(n)]])
    tc = y * Bq.inv(); fl = [int(tc[0, i].p // tc[0, i].q) for i in range(n)]
    x0 = tuple(sum(fl[i] * B[i][j] for i in range(n)) for j in range(n))
    inW = lambda x: all(-wp[j] <= x[j] - o[j] <= ell[j] + wm[j] for j in range(n))
    assert inW(x0), "x0 not in W"
    seen = {x0}; dq = deque([x0]); found = []
    while dq:
        x = dq.popleft()
        if all(0 <= x[j] - o[j] < ell[j] for j in range(n)): found.append(x[0])
        for b in B:
            for sg in (1, -1):
                z = tuple(x[j] + sg * b[j] for j in range(n))
                if z not in seen and inW(z): seen.add(z); dq.append(z)
    assert len(seen) <= Wb, ("|W| bound fails", len(seen), float(Wb))
    assert sorted(found) == Sol, ("(ii) completeness fails", sl, lists, K, B, sorted(found), Sol)
    return ("ok", len(Sol))

cnt = {"ok": 0, "skipped": 0}; nonempty = 0
for mode in ("lll", "mild", "wild"):
    for m in (1, 2, 3, 4):
        for it in range(400 if m < 4 else 150):
            r, z = test(m, 25 if m < 3 else 12, mode); cnt[r] += 1; nonempty += (z > 0 and r == "ok")
print("Theorem A (i),(ii),(iv): all assertions passed;", cnt, "completed searches with Sol nonempty:", nonempty)

# phi minimum
t = (3 ** .5 - 1) / 2; phi = lambda t: math.log((1 + 2 * t) / (t * (1 - t)))
print("phi(t*) =", phi(t), "ln(4+2sqrt3) =", math.log(4 + 2 * 3 ** .5), "min on grid:", min(phi(i / 100000) for i in range(1, 100000)))
print("2e^(5/6) =", 2 * math.exp(5 / 6))
# (iii) inequalities for n = 1..2000
ok = all((1 + 1 / (2 * n)) ** n <= math.exp(.5) and (1 - 1 / (4 * n)) ** -n <= math.exp(1 / 3) + 1e-15 and (1 + 1 / (4 * n)) ** n <= math.exp(.25) for n in range(1, 2001))
print("(iii) elementary inequalities n=1..2000:", ok, " n=1 value (1-1/4)^-1 =", 4 / 3, "<= e^(1/3) =", math.exp(1 / 3))

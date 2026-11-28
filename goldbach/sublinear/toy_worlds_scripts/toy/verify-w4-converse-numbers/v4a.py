# Theorem A stress test on small instances with ARBITRARY bases (verifier's own implementation).
import math, random, itertools, numpy as np, flint
from fractions import Fraction
from collections import deque
random.seed(1234)
def rand_unimodular(n, steps):
    U = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(steps):
        i, j = random.sample(range(n), 2); c = random.choice((-2, -1, 1, 2))
        U[i] = [a + c * b for a, b in zip(U[i], U[j])]
        if random.random() < 0.2: U[i] = [-a for a in U[i]]
    return U
def test(sl, lists, K, steps):
    m = len(sl); n = m + 1
    el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]
    ell = [K] + [L for (a, d, L) in lists]; o = [0] + [e * a for e, (a, d, L) in zip(el, lists)]   # o not reduced mod s (as in the statement)
    tri = [[1] + el] + [[0] * (i + 1) + [-s] + [0] * (m - i - 1) for i, s in enumerate(sl)]
    U = rand_unimodular(n, steps); B = [[sum(U[i][k] * tri[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    if steps < 0:
        B = flint.fmpz_mat(tri).lll(); B = [[int(B[i, j]) for j in range(n)] for i in range(n)]
    wp = [sum(max(B[i][j], 0) for i in range(n)) for j in range(n)]; wm = [sum(max(-B[i][j], 0) for i in range(n)) for j in range(n)]
    tau = [(wp[j] + wm[j]) / ell[j] for j in range(n)]
    # brute force solutions
    sol = set()
    for k in range(K):
        if all(((k - a) * e) % s < L for s, e, (a, d, L) in zip(sl, el, lists)):
            # also check the original definition k mod s in {a + d t}
            assert all(any((a + d * t - k) % s == 0 for t in range(L)) for s, (a, d, L) in zip(sl, lists))
            sol.add(k)
        else:
            assert not all(any((a + d * t - k) % s == 0 for t in range(L)) for s, (a, d, L) in zip(sl, lists))
    E = K * math.prod(L / s for s, (a, d, L) in zip(sl, lists))
    lowb = E * math.prod(max(0, 1 - t) for t in tau); upb = E * math.prod(1 + t for t in tau)
    assert lowb <= len(sol) + 1e-9 and len(sol) <= upb + 1e-9, ("count bounds", lowb, len(sol), upb)
    # start
    Bq = flint.fmpq_mat(flint.fmpz_mat(B)); y = flint.fmpq_mat([[flint.fmpq(2 * o[j] + ell[j], 2) for j in range(n)]]); tc = y * Bq.inv()
    fl = [int(tc[0, i].p // tc[0, i].q) for i in range(n)]
    x0 = tuple(sum(fl[i] * B[i][j] for i in range(n)) for j in range(n))
    inW = lambda x: all(-wp[j] <= x[j] - o[j] <= ell[j] + wm[j] for j in range(n))
    assert inW(x0)
    seen = {x0}; dq = deque([x0]); found = set()
    while dq:
        x = dq.popleft()
        if all(0 <= x[j] - o[j] < ell[j] for j in range(n)): found.add(x[0])
        for b in B:
            for sg in (1, -1):
                zz = tuple(x[j] + sg * b[j] for j in range(n))
                if zz not in seen and inW(zz): seen.add(zz); dq.append(zz)
        if len(seen) > 400000: return None
    assert found == sol, ("completeness", len(found), len(sol))
    assert len(seen) <= E * math.prod(1 + 2 * t for t in tau) + 1e-9, "W bound"
    # floor (iv)
    assert math.prod(tau) >= 1 / E - 1e-12
    return len(sol), len(seen), max(tau)
cnt = 0; skipped = 0; worst = 0
small = [5, 7, 8, 9, 11, 13, 15, 16, 17, 19, 23, 25, 29, 31]     # moduli need not be prime or coprime
for trial in range(1500):
    m = random.choice((1, 1, 2, 2, 3)); sl = [random.choice(small) for _ in range(m)]; K = random.randrange(1, 400)
    lists = []
    for s in sl:
        d = random.choice([d for d in range(1, s) if math.gcd(d, s) == 1]); lists.append((random.randrange(s), d, random.randrange(1, s + 1)))
    r = test(sl, lists, K, random.choice((-1, 0, 1, 3, 6, 10)))
    if r is None: skipped += 1
    else: cnt += 1; worst = max(worst, r[2])
print("small instances passed:", cnt, "skipped (search too large):", skipped, "largest tau seen %.1f" % worst)

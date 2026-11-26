# Check of Theorem 1 (characteristic 2) by factorisation.  q = 2^k, N = lam * A^4, A = L_J * B (B monic, given),
# Q monic squarefree of degree d < n with Q' = S^2 and S | A.  r(.) = number of irreducible factors.
#   (b) d odd:                         r(N-Q) = r(Q) + 1 + k*(a + (d^2-1)/8)                       (mod 2)
#   (c) d even, q_{d-1} != 0, n-d >= 4:
#         d = 0 mod 4:                 r(N-Q) = r(Q) + k*(a + d/4)                                  (mod 2)
#         d = 2 mod 4:                 r(N-Q) = r(Q) + k*(a + (d-2)/4) + Tr(q_{d-2}/q_{d-1}^2)      (mod 2)
# Rows tested: every monic irreducible Q of each degree (or a random sample), and random monic squarefree Q.
#   python3 char2_theorem.py k J Bindex lamindex dmin dmax [cap] [nsqf]
import itertools, random, sys
from collections import defaultdict
from flint import fq_default_ctx, fq_default_poly_ctx
k, J, bi, li, dmin, dmax = (int(v) for v in sys.argv[1:7]); q = 2 ** k
cap = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
nsqf = int(sys.argv[8]) if len(sys.argv) > 8 else 300
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; one, zero = F(1), F(0)
def tr(v):
    s = zero; w = v
    for _ in range(k): s += w; w = w * w
    return 1 if s == one else 0
def V(j):
    v = R(1)
    for i in range(1, j + 1):
        g = pow(x, q ** i, None) - x; v = v * (g // v.gcd(g))
    return v
L = R(1)
for m in range(1, J + 1): L = L * V(J // m)
g_ = F([0, 1] + [0] * (k - 2)) if k > 1 else one   # the generator z of F_q over F_2
Bs = [R(1), x, x + 1, x ** 2 + x + 1, x ** 3 + g_ * x + 1, x ** 5 + x ** 2 + g_]
B = Bs[bi]; A = L * B; a = A.degree()
lam = [one, g_, g_ + one][li]
N = lam * A ** 4; n = N.degree()
print(f"F_{q}: A = L_{J} * ({B}), deg L_{J} = {L.degree()}, a = {a}, lam = {lam}, N = lam*A^4, n = {n}")
random.seed(7)
def nfac(f): return sum(m for _, m in f.factor()[1])
def predict(Q, rQ):
    d = Q.degree(); qc = Q.coeffs()
    if d % 2 == 1: return (rQ + 1 + k * (a + (d * d - 1) // 8)) % 2
    if qc[d - 1] == zero or n - d < 4: return None
    if d % 4 == 0: return (rQ + k * (a + d // 4)) % 2
    return (rQ + k * (a + (d - 2) // 4) + tr(qc[d - 2] / qc[d - 1] ** 2)) % 2
def Sof(Q):
    co = Q.derivative().coeffs()
    return R([c ** (q // 2) for c in co[0::2]]) if co else R(0)
tot_checked = tot_bad = 0; forced_all = 0; rows_all = 0
for d in range(dmin, dmax + 1):
    rows = []
    if q ** d <= 70000:
        for c in itertools.product(els, repeat=d):
            Q = R(list(c) + [one])
            if Q.is_irreducible(): rows.append(Q)
    else:
        seen = set()
        while len(rows) < cap:
            c = tuple(random.randrange(q) for _ in range(d))
            if c in seen: continue
            seen.add(c); Q = R([els[i] for i in c] + [one])
            if Q.is_irreducible(): rows.append(Q)
    total = len(rows)
    if total > cap: rows = random.sample(rows, cap)
    st = defaultdict(int)
    for Q in rows:
        S = Sof(Q); hyp = (S != 0 and A % S == 0)
        r = nfac(N - Q); p_ = predict(Q, 1) if hyp else None
        if p_ is None:
            st[("no formula (S does not divide A)" if not hyp else "no formula (q_(d-1) = 0)", r % 2)] += 1
        else:
            st[("formula", r % 2)] += 1; tot_checked += 1
            if p_ != r % 2: tot_bad += 1; st["BAD"] += 1
    ev = sum(v for (key, v) in st.items() if key != "BAD" and key[1] == 0)
    forced_all += ev; rows_all += len(rows)
    # random squarefree (not necessarily irreducible) Q of this degree
    sq_checked = sq_bad = 0; tries = 0
    while sq_checked < nsqf and tries < 20 * nsqf:
        tries += 1
        Q = R([random.choice(els) for _ in range(d)] + [one])
        if Q.gcd(Q.derivative()).degree() != 0: continue
        S = Sof(Q)
        if S == 0 or A % S != 0: continue
        rQ = nfac(Q); p_ = predict(Q, rQ)
        if p_ is None: continue
        f = N - Q; assert f.gcd(f.derivative()).degree() == 0
        sq_checked += 1; sq_bad += (nfac(f) % 2 != p_)
    tot_checked += sq_checked; tot_bad += sq_bad
    print(f"  d = {d}: {total} monic irreducible rows, {len(rows)} tested, N - Q reducible-by-parity (r even) for {ev}; "
          + "; ".join(f"{key[0]}: r {'even' if key[1] == 0 else 'odd'} {v}" for key, v in sorted(st.items(), key=str) if key != "BAD")
          + f"; BAD {st['BAD']}; squarefree Q: {sq_checked} checked, {sq_bad} bad")
print(f"TOTAL formula checks {tot_checked}, disagreements {tot_bad}; irreducible rows tested {rows_all}, with r even {forced_all}")

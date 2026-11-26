# Characteristic 2: parity of the number r of irreducible factors of N - Q for N = lam * A^4 over F_q, q = 2^k.
# Every Q in F_q[x] is E^2 + x S^2 and Q' = S^2 with deg S <= (deg Q - 1)/2.
# Claim tested (odd d proved in the page):  if S | A, A monic of degree a, d = deg Q odd, Q squarefree, then
#       r(N - Q) = r(Q) + 1 + k * (a + (d^2-1)/8)   (mod 2).
# For even d the script tabulates the parity against candidate invariants of the row.
#
#   python3 char2_parity.py k J t mode dmin dmax [cap] [extra]
#     A = B_J * x^t * (x+1)^extra,  B_J = L_J (lcm of all polynomials of degree <= J) if mode = L, V_J (product of all
#     monic irreducibles of degree <= J) if mode = V.  Rows: all monic irreducible Q with dmin <= deg Q <= dmax
#     (a random sample of cap per degree if there are more).
import itertools, random, sys
from collections import defaultdict
from flint import fq_default_ctx, fq_default_poly_ctx

k, J, t = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); mode = sys.argv[4]
dmin, dmax = int(sys.argv[5]), int(sys.argv[6]); cap = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
extra = int(sys.argv[8]) if len(sys.argv) > 8 else 0
q = 2 ** k
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]
one, zero = F(1), F(0)
def tr(v):
    s = zero; w = v
    for _ in range(k): s += w; w = w * w
    assert s == zero or s == one
    return 1 if s == one else 0
def fsqrt(v): return v ** (q // 2)
def V(j):
    v = R(1)
    for i in range(1, j + 1):
        g = pow(x, q ** i, None) - x
        v = v * (g // v.gcd(g))
    return v
if mode == "V": B = V(J)
else:
    B = R(1)
    for m in range(1, J + 1): B = B * V(J // m)          # lcm of all polynomials of degree <= J
A = B * x ** t * (x + 1) ** extra
a = A.degree(); N = A ** 4; n = N.degree()
assert N.derivative() == 0
print(f"F_{q}: A = {'L' if mode != 'V' else 'V'}_{J} * x^{t} * (x+1)^{extra}, a = deg A = {a}, N = A^4, n = {n}")
random.seed(1)
bad_odd = 0; n_odd = 0
for d in range(dmin, dmax + 1):
    rows = []
    if q ** d <= 300000:
        for c in itertools.product(els, repeat=d):
            Q = R(list(c) + [one])
            if Q.is_irreducible(): rows.append(Q)
    else:
        seen = set()
        while len(rows) < cap:
            c = tuple(random.randrange(q) for _ in range(d))
            if c in seen: continue
            seen.add(c)
            Q = R([els[i] for i in c] + [one])
            if Q.is_irreducible(): rows.append(Q)
    total = len(rows)
    if total > cap: rows = random.sample(rows, cap)
    tab = defaultdict(lambda: [0, 0, 0])
    for Q in rows:
        D = Q.derivative()
        co = D.coeffs()
        S = R([fsqrt(co[2 * i]) for i in range((len(co) + 1) // 2)]) if len(co) else R(0)
        assert S * S == D
        e = D.degree()
        sdiv = (A % S == 0)
        rad = S
        while True:
            g = rad.gcd(rad.derivative())
            if g.degree() <= 0: break
            # in char 2 use squarefree part via factorisation (small degree)
            rad = R(1)
            for f_, _ in S.factor()[1]: rad = rad * f_
            break
        raddiv = (A % rad == 0)
        f = N - Q
        fac = f.factor()[1]
        r = sum(m for _, m in fac)
        sqf = all(m == 1 for _, m in fac)
        if d % 2 == 1:
            key = ("odd", e, sdiv, raddiv, sqf)
            pred = (1 + 1 + k * (a + (d * d - 1) // 8)) % 2     # r(Q) = 1
            if sdiv:
                n_odd += 1; bad_odd += (r % 2 != pred)
            tab[key][2] = pred
        else:
            qc = Q.coeffs()
            q1 = qc[d - 1]; q2 = qc[d - 2]
            if q1 != zero: inv = tr(q2 / (q1 * q1))
            else: inv = "q1=0"
            key = ("even", e, sdiv, raddiv, sqf, inv)
        tab[key][r % 2] += 1
    print(f"  degree {d}: {total} monic irreducibles, {len(rows)} tested")
    for key in sorted(tab, key=str):
        ev, od, pred = tab[key]
        if key[0] == "odd":
            print(f"    deg Q' = {key[1]}, S|A {key[2]}, rad(S)|A {key[3]}, N-Q squarefree {key[4]}: r even {ev}, r odd {od}"
                  + (f"   [formula: r {'even' if pred == 0 else 'odd'}]" if key[2] else ""))
        else:
            print(f"    deg Q' = {key[1]}, S|A {key[2]}, rad(S)|A {key[3]}, N-Q squarefree {key[4]}, Tr(q_(d-2)/q_(d-1)^2) = {key[5]}: r even {ev}, r odd {od}")
print(f"odd-degree rows with S | A: {n_odd} checked, {bad_odd} disagreements with the formula")

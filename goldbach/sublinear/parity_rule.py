# Check, row by row, the Lean session's general parity rule (FunctionField/ParityDesert.lean, even_card_factors_iff):
# over F_q with q a square, lam a non-square, N = lam * V_J^p * x^(p a) of degree n, Q monic irreducible of degree
# d < n with every irreducible factor of Q' of degree <= J, e = deg Q', l = leading coefficient of Q':
#     the number r of irreducible factors of N - Q is even   iff   (-1)^(d + 1 + e) * chi(l)^(n - d) = 1.
# This includes the rows with p | d, which Result 1 left out.
#
#   python3 parity_rule.py p e J a d [max_rows] [seed]
import itertools, random, sys
from flint import fq_default_ctx, fq_default_poly_ctx

p, ex, J, a, d = (int(v) for v in sys.argv[1:6]); cap = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
random.seed(int(sys.argv[7]) if len(sys.argv) > 7 else 1)
q = p ** ex; assert ex % 2 == 0, "q must be a square"
F = fq_default_ctx(p, ex); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(p), repeat=ex)]
lam = next(v for v in els if v != 0 and not v.is_square())
V = R(1)
for j in range(1, J + 1):
    g = pow(x, q ** j, None) - x
    V = V * (g // V.gcd(g))
N = lam * V ** p * x ** (p * a); n = N.degree()
def smooth(f):                     # every irreducible factor of degree <= J
    return all(g.degree() <= J for g, _ in f.factor()[1])
def rows():
    if q ** d <= 200000:
        for c in itertools.product(els, repeat=d): yield R(list(c) + [F(1)])
    else:
        while True: yield R([random.choice(els) for _ in range(d)] + [F(1)])
stats = {}; done = 0; bad = 0
for Q in rows():
    if not Q.is_irreducible(): continue
    D = Q.derivative()
    if D.degree() >= 1 and not smooth(D): continue
    e = D.degree(); l = D.leading_coefficient()
    r = sum(m for _, m in (N - Q).factor()[1])
    chi = 1 if l.is_square() else -1
    predicted_even = ((-1) ** (d + 1 + e)) * (chi ** ((n - d) % 2)) == 1
    key = (e, chi); s = stats.setdefault(key, [0, 0, 0]); s[0] += 1; s[1] += (r % 2 == 0); s[2] += predicted_even
    bad += (r % 2 == 0) != predicted_even; done += 1
    if done >= cap: break
print(f"F_{q} (p = {p}), J = {J}, N = lam * V_J^{p} * x^{p*a}, deg N = {n}, lam non-square; rows: monic irreducible of degree {d} with a {J}-smooth derivative"
      + (" [p divides d]" if d % p == 0 else ""))
for (e, chi), (cnt, ev, pe) in sorted(stats.items()):
    print(f"  deg Q' = {e}, chi(lc Q') = {chi:+d}: {cnt} rows, r even for {ev}, rule predicts even for {pe}")
print(f"  {done} rows checked, {bad} disagreements with the rule")

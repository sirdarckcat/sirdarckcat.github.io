# Johnson guarantee (full agreement) with E|C(L)| >= Emin on random lists: compare the unknowns M with
# (a) q^n and (b) the information-set candidate count  min_I q^n prod_{i in I} rho_i  (T_I <= n)  [Theorem 3 (O1)].
import itertools, math
from sympy import divisors, mobius
def Iq(q, e): return sum(mobius(e // d) * q ** d for d in divisors(e)) // e
def Mn(n, D):
    J = (D - 1) // (n - 1); return (J + 1) * D - (n - 1) * J * (J + 1) // 2
def infoset(q, n, used):
    # used: list of (e, m, l); knapsack over total degree <= n minimising sum ln rho
    best = [0.0] + [0.0] * n   # best[t] = min sum ln rho with total degree <= t
    items = []
    for e, m_, l_ in used:
        items += [(e, math.log(l_ / q ** e))] * m_
    dp = [0.0] * (n + 1)
    for e, v in items:
        for t in range(n, e - 1, -1):
            dp[t] = min(dp[t], dp[t - e] + v)
    return n * math.log(q) + dp[n]
res = {}
for q in (2, 3, 4, 5, 7, 8, 9, 11, 13):
    dmax = {2: 5, 3: 3, 4: 2, 5: 2, 7: 2, 8: 2, 9: 1, 11: 1, 13: 1}[q]
    I = [Iq(q, e) for e in range(1, dmax + 1)]
    def mchoices(Ie): return sorted(set([1, 2, 3, Ie // 2, Ie - 1, Ie]) & set(range(1, Ie + 1)))
    def lchoices(e):
        Q = q ** e
        return sorted(set([1, 2, 3, 4, Q // 3, Q // 2, (2 * Q) // 3, Q - 4, Q - 3, Q - 2, Q - 1]) & set(range(1, Q)))
    per = [[(0, 1)] + [(m_, l_) for m_ in mchoices(I[e - 1]) for l_ in lchoices(e)] for e in range(1, dmax + 1)]
    for combo in itertools.product(*per):
        used = [(e, m_, l_) for e, (m_, l_) in enumerate(combo, 1) if m_ > 0]
        if not used or len(used) > 3: continue
        mass = sum(m_ * e / l_ for e, m_, l_ in used)
        if mass <= 1: continue
        lnrho = sum(m_ * math.log(l_ / q ** e) for e, m_, l_ in used)
        for n in range(2, int(math.ceil(mass)) + 1):
            if not (n - 1 < mass): continue
            lnE = n * math.log(q) + lnrho
            if lnE < -1e-9: continue
            bestM = None
            for s in itertools.product(range(1, 15), repeat=len(used)):
                D = sum(m_ * e * s_ for (e, m_, l_), s_ in zip(used, s))
                C = sum(m_ * l_ * e * s_ * (s_ + 1) // 2 for (e, m_, l_), s_ in zip(used, s))
                M = Mn(n, D)
                if M > C and (bestM is None or M < bestM): bestM = M
            if bestM is None: continue
            lnIS = infoset(q, n, used)
            cls = "E>=2" if lnE >= math.log(2) - 1e-9 else "1<=E<2"
            for name, ref in (("q^n", n * math.log(q)), ("infoset", lnIS), ("E", lnE)):
                key = (cls, name)
                r = math.log(bestM) - ref
                if key not in res or r < res[key][0]:
                    res[key] = (r, q, n, used, bestM, math.exp(lnE), math.exp(lnIS))
            res[("count", cls)] = (res.get(("count", cls), (0,))[0] + 1,)
for k in sorted(res, key=str):
    v = res[k]
    if k[0] == "count": print(k, v[0]); continue
    print(f"{k}: min M/ref = {math.exp(v[0]):.3f} at q={v[1]} n={v[2]} (deg,places,list)={v[3]} M={v[4]} E={v[5]:.2f} infoset candidates={v[6]:.1f}")

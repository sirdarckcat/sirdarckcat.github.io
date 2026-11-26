# Search: Johnson guarantee (M_n(D) > C, D = full agreement) with E|C(L)| = q^n prod rho_i >= 1 for random lists.
# Is M < q^n ever possible there?  pure arithmetic.
import itertools, math
from sympy import divisors, mobius
def Iq(q, e): return sum(mobius(e // d) * q ** d for d in divisors(e)) // e
def Mn(n, D):
    J = (D - 1) // (n - 1); return (J + 1) * D - (n - 1) * J * (J + 1) // 2
best = {}
found_abundant = 0; found_cheap = []
for q in (2, 3, 4, 5, 7, 8, 9, 11, 13):
    dmax = {2: 4, 3: 3, 4: 2, 5: 2, 7: 2, 8: 2, 9: 1, 11: 1, 13: 1}[q]
    I = [Iq(q, e) for e in range(1, dmax + 1)]
    # choices per degree: number of places used m_e in {0..I_e} (thinned), list size l_e
    def mchoices(Ie): return sorted(set([0, 1, 2, Ie // 2, Ie - 1, Ie]) & set(range(Ie + 1)))
    def lchoices(e):
        Q = q ** e
        return sorted(set([1, 2, 3, Q // 2, Q - 3, Q - 2, Q - 1]) & set(range(1, Q)))  # proper lists only
    per = []
    for e in range(1, dmax + 1):
        opts = [(0, 1)] + [(m_, l_) for m_ in mchoices(I[e - 1]) if m_ > 0 for l_ in lchoices(e)]
        per.append(opts)
    for combo in itertools.product(*per):
        mass = sum(m_ * e / l_ for e, (m_, l_) in enumerate(combo, 1))
        if mass <= 1: continue
        lnrho = sum(m_ * math.log(l_ / q ** e) for e, (m_, l_) in enumerate(combo, 1))
        for n in range(2, int(math.ceil(mass)) + 1):
            if not (n - 1 < mass): continue
            lnE = n * math.log(q) + lnrho
            if lnE < 0: continue           # abundant only
            # least-cost multiplicities among small vectors
            used = [(e, m_, l_) for e, (m_, l_) in enumerate(combo, 1) if m_ > 0]
            bestM = None
            for s in itertools.product(range(1, 13), repeat=len(used)):
                D = sum(m_ * e * s_ for (e, m_, l_), s_ in zip(used, s))
                C = sum(m_ * l_ * e * s_ * (s_ + 1) // 2 for (e, m_, l_), s_ in zip(used, s))
                M = Mn(n, D)
                if M > C and (bestM is None or M < bestM[0]): bestM = (M, s, D, C)
            if bestM is None: continue
            found_abundant += 1
            ratio = bestM[0] / q ** n
            key = (q, n)
            if key not in best or ratio < best[key][0]:
                best[key] = (ratio, combo, bestM, math.exp(lnE))
            if bestM[0] < q ** n: found_cheap.append((q, n, combo, bestM, math.exp(lnE)))
print("abundant (E>=1) configurations inside the Johnson guarantee found:", found_abundant)
print("of which with fewer unknowns than q^n:", len(found_cheap))
for k in sorted(best):
    r, combo, bm, E = best[k]
    print(f"q={k[0]} n={k[1]}: least M/q^n = {r:.2f}  (m_e,l_e)={combo}  M={bm[0]} s={bm[1]} C={bm[3]}  E|C(L)|={E:.2f}")
for x in found_cheap[:20]: print("CHEAP", x)

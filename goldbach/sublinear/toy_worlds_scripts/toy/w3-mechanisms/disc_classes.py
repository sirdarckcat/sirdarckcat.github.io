# Beyond the quadratic character: for N' = 0 the WHOLE discriminant of N - Q is forced, disc(N-Q) = c(n,d,lam) * disc(Q)
# (when N vanishes on the roots of Q').  Does the class of the discriminant modulo 4th powers (q = 1 mod 4) say anything
# about the factorisation type?  Tabulated: for monic irreducible polynomials of each degree over F_5 and F_13, how the
# discriminants fall in the cosets of the 4th powers.  Stickelberger fixes the coset modulo squares; inside it both
# 4th-power cosets occur about equally, so a constant discriminant excludes irreducibility only through its square class.
import itertools
from collections import Counter
from flint import nmod_poly
for p in (5, 13):
    g = next(g for g in range(2, p) if len({pow(g, i, p) for i in range(p - 1)}) == p - 1)
    dlog = {pow(g, i, p): i for i in range(p - 1)}
    for d in range(2, 6 if p == 5 else 4):
        cnt = Counter()
        for c in itertools.product(range(p), repeat=d):
            f = nmod_poly(list(c) + [1], p)
            if len(f.factor()[1]) != 1 or f.factor()[1][0][1] != 1 or f.factor()[1][0][0].degree() != d: continue
            D = int(f.resultant(f.derivative())) * (-1) ** (d * (d - 1) // 2) % p
            cnt[dlog[D] % 4] += 1
        print(f"F_{p}, irreducible of degree {d}: discriminant in g^i * (4th powers), i = 0..3: {[cnt[i] for i in range(4)]}")

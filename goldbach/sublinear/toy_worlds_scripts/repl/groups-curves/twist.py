"""The cheap parities of elliptic curves are residues.  For a fixed E (conductor C) and squarefree d coprime to 2C,
the root number of the quadratic twist E^(d*), d* = +-d = 1 mod 4, depends only on d modulo 4C (w(E^d) = w(E) chi_d'(-C), d' the fundamental
discriminant of Q(sqrt d)).  Checked with PARI for three curves; contrast: the family E_n of rootno.py, where the sign is -mu(n)."""
import sys, math
sys.path.insert(0, "./pylib")
import cypari2
from sympy import factorint
pari = cypari2.Pari()
for name, coef in (("11a1", [0, -1, 1, -10, -20]), ("37a1", [0, 0, 1, -1, 0]), ("389a1", [0, 1, 1, -2, 0])):
    E = pari.ellinit(coef); C = int(pari.ellglobalred(E)[0]); cls = {}; tot = 0; mu_corr = 0
    for d in range(1, 20000):
        if math.gcd(d, 2 * C) != 1: continue
        f = factorint(d)
        if any(e > 1 for e in f.values()): continue
        w = int(pari.ellrootno(pari.elltwist(E, d if d % 4 == 1 else -d)))
        cls.setdefault(d % (4 * C), set()).add(w); tot += 1; mu_corr += w * (-1) ** len(f)
    print(f"{name}: conductor {C}; {tot} twists d < 20000; classes of d mod {4*C} with both signs: {sum(1 for s in cls.values() if len(s) > 1)} of {len(cls)}; mean of w*mu(d) = {mu_corr/tot:+.4f} +- {1/math.sqrt(tot):.4f}")

# Bottom-up round: is the residual set U of a near-floor cover structured modulo the next primes? Over the research session's 300
# covers at 200,000 (89 moduli, all at 1,502-1,503 rows), measure three things at p = 467 ... 499: the heaviest class (what a pin there
# kills); the share of U in the best coset c + (squares) (what a quadratic family can align with; 0.5 is no structure); and the
# share in the heaviest half of the classes (the Poisson level is about 0.69 at 3 rows a class).
#   python3 structure_of_U.py
import numpy as np
Q = 200000
s = np.ones(Q, bool); s[:2] = False
for i in range(2, int(Q ** 0.5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s)[0]; P = P[P > 2]
covers = [(int(t[1]), [tuple(map(int, w.split(":"))) for w in t[2:]]) for t in (l.split() for l in open("q200000_m89.txt")) if t and t[0] == "COVER"]
for p in (467, 479, 487, 491, 499):
    mx, qrs, hf = [], [], []
    qr = np.zeros(p, bool); qr[(np.arange(1, p) ** 2) % p] = True; qi = np.nonzero(qr)[0]
    for rows, pairs in covers:
        unc = np.ones(len(P), bool)
        for r, a in pairs: unc &= (P % r) != a
        U = P[unc]; c = np.bincount(U % p, minlength=p)
        mx.append(c.max()); qrs.append(max(c[(qi + c0) % p].sum() for c0 in range(p)) / len(U)); hf.append(np.sort(c)[::-1][: p // 2].sum() / len(U))
    print(f"p = {p}: heaviest class {np.mean(mx):.1f} (max {max(mx)}); best square-coset share {np.mean(qrs):.3f} (max {max(qrs):.3f}); "
          f"heaviest-half share {np.mean(hf):.3f} (max {max(hf):.3f})")

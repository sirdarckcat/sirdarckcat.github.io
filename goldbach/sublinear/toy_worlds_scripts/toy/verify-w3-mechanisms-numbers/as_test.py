# Theorem 3 (Artin-Schreier): counts of rows C(x^p - x) and random test
import random, sys
from ffg import FF
rng = random.Random(5)
for (p, e, cdegs, m, nA) in [(3,1,[1,2,3],12,40), (3,2,[1,2],9,20), (2,2,[1,2,3],10,20), (5,1,[1,2],8,40), (2,1,[1,2,3,4],9,60), (2,3,[1,2],7,20)]:
    K = FF(p, e); x = K.x
    AS = x**p - x
    rows = []
    cnt = {}
    for dc in cdegs:
        c = 0
        for C in K.monics(dc):
            Q = C(AS)
            if Q.is_irreducible():
                rows.append((C, Q)); c += 1
        cnt[dc*p] = c
        # closed form: irreducible C of degree dc with Tr(second coeff) != 0
        c2 = sum(1 for C in K.monics(dc) if C.is_irreducible() and K.tr(C.coeffs()[dc-1]) != K.zero)
        assert c2 == c, (c, c2)
    res = {}
    for trz in (True, False):
        irr = 0; tot = 0; viol = 0; pfac_ok = 0; pfac_n = 0
        for t in range(nA):
            while True:
                A = K.rand_monic(m, rng)
                if (K.tr(A.coeffs()[m-1]) == K.zero) == trz: break
            N = A(AS)
            for (C, Q) in rows:
                if C.degree() > m - 2: continue
                f = N - Q
                tot += 1
                g = A - C
                fi = f.is_irreducible(); gi = g.is_irreducible()
                if fi: irr += 1
                if trz:
                    if fi: viol += 1
                    if gi:
                        lead, fs = f.factor(); pfac_n += 1
                        if len(fs) == p and all(h.degree() == m and mu == 1 for h, mu in fs): pfac_ok += 1
                else:
                    if fi != gi: viol += 1
        res[trz] = (tot, irr, viol, pfac_ok, pfac_n)
    print(f"F_{K.q}: rows C(x^{p}-x) by degree {cnt}; trace 0: pairs {res[True][0]}, irreducible {res[True][1]}, violations {res[True][2]}, 'p factors of degree m' {res[True][3]}/{res[True][4]}; trace != 0: pairs {res[False][0]}, irreducible {res[False][1]}, violations {res[False][2]}")

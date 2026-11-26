import sys, random
sys.path.insert(0, "/tmp/claude-0/-home-user-sirdarckcat-github-io/9ab28896-d478-5e7c-817b-7f69ce9b4074/scratchpad/work/repl/groups-curves/pylib")
import cypari2
pari = cypari2.Pari(); pari.allocatemem(400000000)
random.seed(7)
# (1) root number of E_n for random n in [10^8, 10^9] coprime to 6
fail = 0; cnt = 0; failsf = 0; cntsf = 0; nonsf_dev = 0
for _ in range(600):
    n = random.randrange(10**8, 10**9)
    if n % 2 == 0 or n % 3 == 0: continue
    m = 1 + 1728 * n
    E = pari.ellinit([1, 0, 0, -36 * n, -n])
    assert int(E.disc()) == n * m * m
    w = int(pari.ellrootno(E))
    om = int(pari.omega(n))
    fm = pari.factor(m); corr = 1
    for i in range(len(fm[0])):
        p = int(fm[0][i]); v = int(fm[1][i])
        if v % 2 == 1: corr *= int(pari.kronecker(-1, p))
        if v % 6 in (2, 4): corr *= int(pari.kronecker(-3, p))
    pred = -(-1) ** om * corr
    cnt += 1; fail += (w != pred)
    if int(pari.issquarefree(m)):
        cntsf += 1; failsf += (w != -(-1) ** om)
    else:
        nonsf_dev += (w != -(-1) ** om)
print(f"E_n, random n in [1e8,1e9] coprime to 6: {cnt} curves, full formula fails {fail}; m squarefree: {cntsf}, w=-(-1)^omega fails {failsf}; m not squarefree: {cnt-cntsf}, of which simple formula wrong {nonsf_dev}")
# omega vs Omega: n = p^2 q
bad = 0; c = 0
for p in (5, 7, 11, 13, 17, 19, 23):
    for q in (29, 31, 37, 41, 43):
        n = p * p * q; m = 1 + 1728 * n
        if not int(pari.issquarefree(m)): continue
        w = int(pari.ellrootno(pari.ellinit([1, 0, 0, -36 * n, -n]))); c += 1
        bad += (w != -(-1) ** 2)          # omega = 2 -> -1 ; Omega = 3 would give +1
print(f"n = p^2 q: {c} curves, 'w = -(-1)^omega (distinct primes)' fails {bad}  (so the sign is omega, not Omega / not lambda)")
# (2) twists: w(E^d) = w(E) * kronecker(d, -C) for fundamental d coprime to C
for lab, co in (("11a1",[0,-1,1,-10,-20]), ("37a1",[0,0,1,-1,0]), ("389a1",[0,1,1,-2,0]), ("5077a1",[0,0,1,-7,6])):
    E = pari.ellinit(co); C = int(pari.ellglobalred(E)[0]); w0 = int(pari.ellrootno(E)); f = 0; c = 0
    for _ in range(600):
        d = random.randrange(-10**6, 10**6)
        if d in (0, 1) or not int(pari.isfundamental(d)) or pari.gcd(d, C) != 1: continue
        w = int(pari.ellrootno(pari.elltwist(E, d))); c += 1
        f += (w != w0 * int(pari.kronecker(d, -C)))
    print(f"{lab}: {c} fundamental twists |d|<1e6, w(E^d) = w(E) (d/-C) fails {f}")
# (3) genus theory: 2-rank of Cl(-4n) for odd squarefree n
r1 = r3 = c1 = c3 = 0
for n in range(5, 4000, 2):
    if not int(pari.issquarefree(n)): continue
    cyc = pari.quadclassunit(-4 * n)[1] if n % 4 == 1 else None
    if n % 4 == 1:
        rk = sum(1 for x in cyc if int(x) % 2 == 0); c1 += 1; r1 += (rk == int(pari.omega(n)))
    else:
        # -4n not fundamental: form class group of discriminant -4n; use qfbclassno parity via genera: count ambiguous reduced forms
        D = -4 * n; amb = 0; a = 1
        # reduced forms (a,b,c), |b|<=a<=c ; ambiguous classes: b=0, a=b, or a=c  (primitive)
        import math
        b = 0
        while True:
            # b even since D = 0 mod 4
            if 3 * b * b > -D: break
            t = (b * b - D) // 4
            for a in range(max(b, 1), int(math.isqrt(t)) + 1):
                if t % a == 0:
                    cc = t // a
                    if math.gcd(math.gcd(a, b), cc) == 1 and (b == 0 or a == b or a == cc): amb += 1
            b += 2
        rk = amb.bit_length() - 1; assert amb == 1 << rk
        c3 += 1; r3 += (rk == int(pari.omega(n)) - 1)
print(f"2-rank of Cl(-4n): n=1 mod 4: equals omega(n) in {r1}/{c1}; n=3 mod 4: equals omega(n)-1 in {r3}/{c3}")

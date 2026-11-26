# Miniature with full factorisations: dictionary images of the Stickelberger-Swan parity against lambda(N - q).
# N random even of 32 digits, rows q = odd primes < 3000, m = N - q factored by FLINT.
import random, math, flint, gmpy2, sys
from gmpy2 import mpz, jacobi
random.seed(77)
def digs(m, b):
    d = []
    while m: m, r = divmod(m, b); d.append(int(r))
    return d
def dder(d, b):                       # f'(b) for f = sum d_i x^i
    return sum(i * d[i] * b ** (i - 1) for i in range(1, len(d)))
import sympy
ROWS = list(sympy.primerange(3, 3000))
BASES = (2, 3, 5, 10, 16, 100)
feat = {}; lam = []; isp = []; lpf = []
def add(name, v): feat.setdefault(name, []).append(v)
ident = dict(n=0, par=0, jac=0, mod8=0, sqf=0)
T = int(sys.argv[1]) if len(sys.argv) > 1 else 60
kind = sys.argv[2] if len(sys.argv) > 2 else "generic"
for t in range(T):
    if kind == "generic": N = random.randrange(10 ** 31, 10 ** 32) & ~1
    elif kind == "square": N = (random.randrange(10 ** 15, 10 ** 16) & ~1) ** 2
    elif kind == "cube": N = (random.randrange(2 * 10 ** 10, 4 * 10 ** 10) & ~1) ** 3
    elif kind == "fifth": N = (random.randrange(10 ** 6, 2 * 10 ** 6) & ~1) ** 5
    elif kind == "teich":             # delta_p(N) = 0 mod p for p = 3,5,7,11,13: N^p = N mod p^2
        P = [3, 5, 7, 11, 13]; mod = 1; N = 0
        for p in P:
            a = random.randrange(1, p); w = pow(a, p, p * p)           # Teichmuller lift mod p^2
            assert pow(w, p, p * p) == w
            tt = ((w - N) * pow(mod, -1, p * p)) % (p * p); N += mod * tt; mod *= p * p
        N += mod * random.randrange(10 ** 31 // mod, 10 ** 32 // mod)
        if N % 2: N += mod
        for p in P: assert pow(N, p, p * p) == N % (p * p)
    Nd = {b: digs(N, b) for b in BASES}
    for q in ROWS:
        m = N - q
        fac = flint.fmpz(m).factor()
        Om = sum(e for _, e in fac); l = -1 if Om % 2 else 1
        lam.append(l); isp.append(1 if Om == 1 else 0); lpf.append(int(fac[0][0]))
        # arithmetic derivative identities
        ad = sum(e * (m // int(p)) for p, e in fac)
        ident["n"] += 1; ident["par"] += (ad % 2) == (Om % 2)
        ident["mod8"] += (ad % 8) == (m * sum(e * int(p) for p, e in fac)) % 8
        if all(e == 1 for _, e in fac):
            k3 = sum(1 for p, _ in fac if int(p) % 4 == 3)
            ident["sqf"] += 1; ident["jac"] += jacobi(ad % m, m) == (-1) ** (k3 * (k3 - 1) // 2)
        for b in BASES:
            d = digs(m, b)
            add(f"J_{b} = (f_b'(b) | m)", jacobi(dder(d, b) % m, m))
            # non-canonical representation F = N_b - Q_b (coefficientwise)
            dq = digs(q, b); F = [Nd[b][i] - (dq[i] if i < len(dq) else 0) for i in range(len(Nd[b]))]
            add(f"J'_{b} = ((N_b - Q_b)'(b) | m)", jacobi(dder(F, b) % m, m))
            add(f"Q-only top: (-Q_b'(b) | m)", 0) if False else None
        for b in (10, 16, 100):
            f = flint.fmpz_poly(digs(m, b)); D = int(f.discriminant())
            add(f"K_{b} = (disc f_b | m)", jacobi(D % m, m))
            add(f"sign disc f_{b}", (D > 0) - (D < 0))
            for p in (3, 5, 7, 11, 13):
                if p <= b and b % p == 0: continue
                add(f"(disc f_{b} | {p}) [Stickelberger at {p}]", jacobi(D % p, p))
        add("(-1|m)", jacobi(-1, m)); add("(2|m)", jacobi(2, m)); add("(3|m)", jacobi(3, m))
n = len(lam)
print(f"kind {kind}: {T} targets, {n} integers m = N - q factored; primes {sum(isp)}; mean lambda {sum(lam) / n:+.4f} +- {1 / math.sqrt(n):.4f}")
big = [i for i in range(n) if lpf[i] > 1000]
print(f"  with no prime factor below 1000: {len(big)}; mean lambda {sum(lam[i] for i in big) / len(big):+.4f} +- {1 / math.sqrt(len(big)):.4f}; primes {sum(isp[i] for i in big)}")
print(f"  identities: n' = Omega (mod 2): {ident['par']}/{ident['n']};  n' = n*sopfr(n) (mod 8): {ident['mod8']}/{ident['n']};  (n'|n) = (-1)^C(k3,2) on squarefree: {ident['jac']}/{ident['sqf']}")
print("  feature | nonzero | z against lambda (all) | z against lambda (no factor < 1000) | z against primality (no factor < 1000)")
zs = []
for name, v in feat.items():
    nz = [i for i in range(n) if v[i] != 0]
    z1 = sum(v[i] * lam[i] for i in nz) / math.sqrt(len(nz))
    nb = [i for i in big if v[i] != 0]
    z2 = sum(v[i] * lam[i] for i in nb) / math.sqrt(len(nb))
    # primality: difference of prime rate between v = +1 and v = -1
    a = [isp[i] for i in nb if v[i] == 1]; c = [isp[i] for i in nb if v[i] == -1]
    pr = (sum(a) + sum(c)) / (len(a) + len(c))
    z3 = (sum(a) / len(a) - sum(c) / len(c)) / math.sqrt(pr * (1 - pr) * (1 / len(a) + 1 / len(c))) if a and c else float("nan")
    zs += [z1, z2, z3]
    print(f"  {name} | {len(nz)} | {z1:+.2f} | {z2:+.2f} | {z3:+.2f}")
zs = [z for z in zs if z == z]
print(f"  {len(zs)} z-scores: max |z| {max(abs(z) for z in zs):.2f}, mean z^2 {sum(z * z for z in zs) / len(zs):.2f} (1.00 = no information)")

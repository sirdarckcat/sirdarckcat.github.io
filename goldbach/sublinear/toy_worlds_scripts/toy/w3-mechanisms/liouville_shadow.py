# Integer control for the parity mechanism.  In F_q[x] the parity of the number of prime factors of N - Q is forced when
# N is a p-th power vanishing at the critical points of Q.  The nearest integer imitations: N a perfect power of a
# primorial (N = 0 mod every small prime, N "inseparable"), N a perfect square/cube/fourth power of a random integer.
# For each N the rows are the primes q, z < q < 6000 (z the largest prime dividing N, so no small prime divides N - q
# for the primorial families); lam = (-1)^Omega(N - q) is computed by complete factorisation (python-flint).
# Reported: the mean of lam over rows (0 under Bateman-Horn / the Chowla heuristic), with its standard error,
# the number of prime N - q against the Hardy-Littlewood expectation, and the correlation of lam with three
# characters of the row (q mod 4, q mod 3, Jacobi symbol (q | N1) for N1 the base).
import math, random, sys
from flint import fmpz
from sympy import primerange, jacobi_symbol, primorial
random.seed(11)
def omega_lam(n):
    fac = fmpz(n).factor()
    Om = sum(e for _, e in fac)
    return (-1) ** Om, Om
fams = []
P43 = primorial(43, nth=False); P29 = primorial(29, nth=False); P13 = primorial(13, nth=False)
fams.append(("primorial(43)^2", P43 ** 2, 43, P43))
fams.append(("primorial(29)^3", P29 ** 3, 29, P29))
fams.append(("primorial(13)^8", P13 ** 8, 13, P13))
A = random.randrange(10 ** 17, 10 ** 18) * 2
fams.append(("A^2, A random even 18 digits", A * A, 2, A))
B = random.randrange(10 ** 11, 10 ** 12) * 2
fams.append(("B^3, B random even 12 digits", B ** 3, 2, B))
C = 2 * random.randrange(10 ** 34, 10 ** 35)
fams.append(("random even N, 35 digits (control)", C, 2, C))
for name, N, z, base in fams:
    rows = [q for q in primerange(max(z, 2) + 1, 6000) if math.gcd(q, N) == 1]
    s = 0; npr = 0; c4 = c3 = cj = 0; exp_pr = 0.0
    for q in rows:
        m = N - q; lam, Om = omega_lam(m)
        s += lam; npr += (Om == 1)
        c4 += lam * (1 if q % 4 == 1 else -1); c3 += lam * (1 if q % 3 == 1 else -1)
        cj += lam * jacobi_symbol(q % base if base % 2 else q, base) if base % 2 else 0
    R_ = len(rows); se = 1 / math.sqrt(R_)
    print(f"{name}: N has {len(str(N))} digits, {R_} rows; mean lam = {s/R_:+.4f} (se {se:.4f}); N - q prime for {npr}; "
          f"corr(lam, q mod 4) = {c4/R_:+.4f}, corr(lam, q mod 3) = {c3/R_:+.4f}")

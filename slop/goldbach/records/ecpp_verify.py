#!/usr/bin/env python3
"""Independent verifier for PARI/GP primecert() ECPP certificates.

A PARI ECPP certificate for N is a vector of steps
    [[N_i, t_i, s_i, a_i, [x_i, y_i]], ...]
with N_0 = N. For each step, with m_i = N_i + 1 - t_i and q_i = m_i / s_i
(q_i = N_{i+1}, or for the last step a small proven prime):

  Theorem (Goldwasser–Kilian / Atkin–Morain, as used by PARI):
  Let N > 1, gcd(6, N) = 1... more precisely gcd(disc, N) checks are subsumed
  by the point arithmetic below: we work on E: y^2 = x^3 + a x + b (mod N) with
  b := y_i^2 - x_i^3 - a x_i (mod N). If
    * q_i is prime,
    * q_i > (N_i^{1/4} + 1)^2,
    * P = (x_i, y_i) satisfies [s_i] P = R is a well-defined point != O, and
      [q_i] R = O, with every inversion performed during the computation either
      succeeding (gcd = 1) or -- if a gcd in (1, N_i) appears -- exhibiting a
      factor of N_i (then N_i is composite: FAIL),
  then N_i is prime.

We do scalar multiplication in Jacobian-free affine coordinates with explicit
gcd checks, so any nontrivial gcd surfaces. The chain must terminate at a
q_last < 2^64 which we prove prime by deterministic Miller-Rabin (with the
verified base set for < 3.3e24) after trial division.

Usage: ecpp_verify.py cert.json  (cert as JSON list-of-lists, integers as
strings or ints).  Exits 0 and prints PRIME iff the certificate is valid for
the top-level N printed.
"""
import json, math, sys

def egcd(a, b):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        qt, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - qt * x1
        y0, y1 = y1, y0 - qt * y1
    return a, x0, y0

class CompositeFactor(Exception):
    pass

def inv_mod(z, n):
    z %= n
    g, x, _ = egcd(z, n)
    if g != 1:
        raise CompositeFactor(g)
    return x % n

def ec_add(P, Qp, a, n):
    """Affine addition on y^2=x^3+ax+b mod n. None = point at infinity."""
    if P is None: return Qp
    if Qp is None: return P
    x1, y1 = P; x2, y2 = Qp
    if (x1 - x2) % n == 0:
        if (y1 + y2) % n == 0:
            return None
        lam = (3 * x1 * x1 + a) * inv_mod(2 * y1, n) % n
    else:
        lam = (y2 - y1) * inv_mod(x2 - x1, n) % n
    x3 = (lam * lam - x1 - x2) % n
    y3 = (lam * (x1 - x3) - y1) % n
    return (x3, y3)

def ec_mul(k, P, a, n):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a, n)
        P = ec_add(P, P, a, n)
        k >>= 1
    return R

SMALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def mr_witness(n, a):
    if n % a == 0: return n != a
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    x = pow(a, d, n)
    if x in (1, n - 1): return False
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1: return False
    return True  # a witnesses compositeness

def is_prime_small(n):
    """Deterministic for n < 3.317e24 (verified MR base set)."""
    assert n < 3317044064679887385961981, "out of deterministic MR range"
    if n < 2: return False
    for p in SMALL_PRIMES:
        if n % p == 0: return n == p
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]:
        if n == a: return True
        if mr_witness(n, a): return False
    return True

def isqrt4_bound(n):
    """(n^{1/4}+1)^2, computed exactly with isqrt."""
    r = math.isqrt(math.isqrt(n))
    while (r + 1) ** 4 <= n: r += 1   # r = floor(n^{1/4})
    return (r + 1) ** 2

def verify(cert):
    cert = [[int(v) if not isinstance(v, list) else [int(w) for w in v] for v in step] for step in cert]
    top = cert[0][0]
    for idx, step in enumerate(cert):
        N, t, s, a, (x, y) = step
        if N < 2 or math.gcd(N, 6) != 1:
            return False, f"step {idx}: N divisible by 2 or 3"
        m = N + 1 - t
        if s <= 0 or m % s != 0:
            return False, f"step {idx}: s does not divide m"
        q = m // s
        # Hasse check on t keeps the certificate honest
        if t * t > 4 * N:
            return False, f"step {idx}: |t| violates Hasse bound"
        if q <= isqrt4_bound(N):
            return False, f"step {idx}: q too small ((N^1/4+1)^2 test)"
        b = (y * y - x * x * x - a * x) % N
        disc = (4 * a * a * a + 27 * b * b) % N
        g = math.gcd(disc, N)
        if g != 1:
            return False, f"step {idx}: singular curve gcd={g}"
        try:
            R = ec_mul(s, (x % N, y % N), a, N)
            if R is None:
                return False, f"step {idx}: [s]P = O, invalid"
            if ec_mul(q, R, a, N) is not None:
                return False, f"step {idx}: [q][s]P != O"
        except CompositeFactor as e:
            return False, f"step {idx}: N composite, factor gcd={e.args[0]}"
        # link to next step
        if idx + 1 < len(cert):
            if cert[idx + 1][0] != q:
                return False, f"step {idx}: chain broken (q != next N)"
        else:
            if not is_prime_small(q):
                return False, f"step {idx}: final q={q} not proven prime"
    return True, top

if __name__ == "__main__":
    cert = json.load(open(sys.argv[1]))
    ok, info = verify(cert)
    if ok:
        print(f"PRIME {info}")
        sys.exit(0)
    print(f"INVALID: {info}")
    sys.exit(1)

"""Independent ECPP certificate verifier (no PARI involvement).

Verifies a PARI/GP `primecert` Atkin-Morain certificate using only
gmpy2 integer arithmetic with Jacobian projective coordinates, so no
modular inversions are needed during scalar multiplication.

Certificate format (PARI): [[N, t, s, a4, [x, y]], ...] where for each
step, with m = N + 1 - t and q = m / s:
  - the curve is y^2 = x^3 + a4 x + a6 (mod N), a6 fixed by the point;
  - q > (N^(1/4) + 1)^2;
  - U = [s]P is well-defined and != O;  V = [q]U = O.
By Goldwasser-Kilian, N is prime provided q is prime, which the next
step certifies (recursion ends below 2^64 where BPSW is deterministic).

Soundness notes: any non-invertible denominator would surface as a
nontrivial gcd(Z, N); we require gcd(Z_U, N) = 1 exactly, and Z_V = 0
(mod N) for the point at infinity.  |t| <= 2 sqrt(N) (Hasse) is also
enforced.

Usage: ecpp_check.py cert.gp expected_candidate.txt
Exits 0 with "INDEPENDENT ECPP CHECK PASSED" iff the certificate is
valid AND its top-level candidate equals the expected integer.
"""

import sys

import gmpy2
from gmpy2 import mpz, gcd, isqrt


def parse_cert(path):
    txt = open(path).read().strip()
    if txt.endswith(";"):
        txt = txt[:-1]
    depth, tok, out = 0, "", []
    stack = [out]
    for ch in txt:
        if ch == "[":
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif ch in ",]":
            if tok.strip():
                stack[-1].append(mpz(tok.strip()))
            tok = ""
            if ch == "]":
                stack.pop()
        elif ch.isspace() or ch == '"':
            continue
        else:
            tok += ch
    assert len(out) == 1
    return out[0]


def jac_dbl(X, Y, Z, a, n):
    if Z == 0 or Y == 0:
        return (mpz(1), mpz(1), mpz(0))
    YY = Y * Y % n
    S = 4 * X * YY % n
    Z2 = Z * Z % n
    M = (3 * X * X + a * Z2 * Z2) % n
    X2 = (M * M - 2 * S) % n
    Y2 = (M * (S - X2) - 8 * YY * YY) % n
    Z2_ = 2 * Y * Z % n
    return (X2, Y2, Z2_)


def jac_add(X1, Y1, Z1, X2, Y2, Z2, a, n):
    if Z1 == 0:
        return (X2, Y2, Z2)
    if Z2 == 0:
        return (X1, Y1, Z1)
    Z1Z1 = Z1 * Z1 % n
    Z2Z2 = Z2 * Z2 % n
    U1 = X1 * Z2Z2 % n
    U2 = X2 * Z1Z1 % n
    S1 = Y1 * Z2 * Z2Z2 % n
    S2 = Y2 * Z1 * Z1Z1 % n
    if U1 == U2:
        if S1 != S2:
            return (mpz(1), mpz(1), mpz(0))
        return jac_dbl(X1, Y1, Z1, a, n)
    H = (U2 - U1) % n
    R = (S2 - S1) % n
    HH = H * H % n
    HHH = H * HH % n
    V = U1 * HH % n
    X3 = (R * R - HHH - 2 * V) % n
    Y3 = (R * (V - X3) - S1 * HHH) % n
    Z3 = Z1 * Z2 * H % n
    return (X3, Y3, Z3)


def jac_mul(k, X, Y, Z, a, n):
    RX, RY, RZ = mpz(1), mpz(1), mpz(0)
    QX, QY, QZ = X, Y, Z
    while k:
        if k & 1:
            RX, RY, RZ = jac_add(RX, RY, RZ, QX, QY, QZ, a, n)
        QX, QY, QZ = jac_dbl(QX, QY, QZ, a, n)
        k >>= 1
    return (RX, RY, RZ)


def verify_step(N, t, s, a4, x, y):
    assert N > 1 and gcd(N, 6) == 1
    r = isqrt(4 * N)
    assert t * t <= 4 * N or abs(t) <= r + 1, "Hasse violated"
    m = N + 1 - t
    assert s > 0 and m % s == 0
    q = m // s
    root4 = isqrt(isqrt(N))
    assert q > (root4 + 1) ** 2, "q too small for Goldwasser-Kilian"
    a6 = (y * y - x * x * x - a4 * x) % N
    disc = (4 * a4 * a4 * a4 + 27 * a6 * a6) % N
    assert gcd(disc, N) == 1, "singular curve"
    UX, UY, UZ = jac_mul(int(s), mpz(x), mpz(y), mpz(1), mpz(a4), N)
    assert gcd(UZ, N) == 1, "[s]P not well-defined / = O"
    VX, VY, VZ = jac_mul(int(q), UX, UY, UZ, mpz(a4), N)
    assert VZ % N == 0, "[m]P != O"
    return q


def main():
    cert = parse_cert(sys.argv[1])
    expected = mpz(open(sys.argv[2]).read().strip())
    assert mpz(cert[0][0]) == expected, (
        "BINDING FAILURE: certificate top-level candidate != expected")
    current = expected
    for i, step in enumerate(cert):
        N, t, s, a4, pt = step
        assert mpz(N) == current, f"chain broken at step {i}"
        current = verify_step(mpz(N), mpz(t), mpz(s), mpz(a4),
                              mpz(pt[0]), mpz(pt[1]))
        if i % 50 == 0:
            print(f"  step {i}: {len(str(N))} digits ok", flush=True)
    assert current < 2 ** 64, f"final q has {len(str(current))} digits"
    assert gmpy2.is_prime(int(current)), "final small prime fails BPSW"
    print(f"chain length {len(cert)}, final prime {current}")
    print("INDEPENDENT ECPP CHECK PASSED")


if __name__ == "__main__":
    main()

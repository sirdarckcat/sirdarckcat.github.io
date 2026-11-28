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

import re
import sys

import gmpy2
from gmpy2 import mpz, gcd

_TOKEN_RE = re.compile(r"\s*(?:(\[)|(\])|(,)|(;)|([+-]?[0-9]+))", re.ASCII)
_WS_END_RE = re.compile(r"\s*\Z", re.ASCII)
_INT_TEXT_RE = re.compile(r"\s*[+-]?[0-9]+\s*", re.ASCII)
_MAX_CERT_DEPTH = 16


def _tokenize_cert(txt):
    tokens = []
    pos = 0
    n = len(txt)
    while pos < n:
        if _WS_END_RE.match(txt, pos):
            break
        m = _TOKEN_RE.match(txt, pos)
        if m is None:
            raise ValueError(
                f"invalid token in certificate at offset {pos}: {txt[pos:pos + 20]!r}"
            )
        if m.group(1) is not None:
            tokens.append(("[", None))
        elif m.group(2) is not None:
            tokens.append(("]", None))
        elif m.group(3) is not None:
            tokens.append((",", None))
        elif m.group(4) is not None:
            tokens.append((";", None))
        else:
            tokens.append(("INT", mpz(m.group(5))))
        pos = m.end()
    return tokens


def parse_cert(path):
    with open(path, "r", encoding="utf-8") as fh:
        txt = fh.read()
    tokens = _tokenize_cert(txt)
    if not tokens:
        raise ValueError("empty certificate input")
    idx = 0

    def parse_list(depth):
        nonlocal idx
        if depth > _MAX_CERT_DEPTH:
            raise ValueError("certificate nesting too deep")
        if idx >= len(tokens) or tokens[idx][0] != "[":
            raise ValueError("expected '[' to start list")
        idx += 1
        items = []
        if idx < len(tokens) and tokens[idx][0] == "]":
            idx += 1
            return items
        while True:
            items.append(parse_value(depth + 1))
            if idx >= len(tokens):
                raise ValueError("unclosed '[' in certificate")
            kind = tokens[idx][0]
            if kind == ",":
                idx += 1
            elif kind == "]":
                idx += 1
                return items
            else:
                raise ValueError(f"expected ',' or ']' in list, got {kind!r}")

    def parse_value(depth):
        nonlocal idx
        if idx >= len(tokens):
            raise ValueError("unexpected end of certificate")
        kind, val = tokens[idx]
        if kind == "INT":
            idx += 1
            return val
        if kind == "[":
            return parse_list(depth)
        raise ValueError(f"unexpected token {kind!r} where value expected")

    cert = parse_list(0)
    if idx < len(tokens) and tokens[idx][0] == ";":
        idx += 1
    if idx != len(tokens):
        raise ValueError(f"unexpected trailing token {tokens[idx][0]!r} in certificate")
    return cert


def jac_dbl(X, Y, Z, a, n):
    Z %= n
    if Z == 0:
        return (mpz(1), mpz(1), mpz(0))
    Y %= n
    if Y == 0:
        assert gcd(Z, n) == 1, "degenerate Z with Y == 0"
        return (mpz(1), mpz(1), mpz(0))
    Z2_ = 2 * Y * Z % n
    assert gcd(Z2_, n) == 1, "nontrivial gcd(2YZ, n) in jac_dbl"
    YY = Y * Y % n
    S = 4 * X * YY % n
    Z2 = Z * Z % n
    M = (3 * X * X + a * Z2 * Z2) % n
    X2 = (M * M - 2 * S) % n
    Y2 = (M * (S - X2) - 8 * YY * YY) % n
    return (X2, Y2, Z2_)


def jac_add(X1, Y1, Z1, X2, Y2, Z2, a, n):
    Z1 %= n
    Z2 %= n
    if Z1 == 0:
        if Z2 != 0:
            assert gcd(Z2, n) == 1, "degenerate Z2 in jac_add"
            return (X2 % n, Y2 % n, Z2)
        return (mpz(1), mpz(1), mpz(0))
    if Z2 == 0:
        assert gcd(Z1, n) == 1, "degenerate Z1 in jac_add"
        return (X1 % n, Y1 % n, Z1)
    Z1Z1 = Z1 * Z1 % n
    Z2Z2 = Z2 * Z2 % n
    U1 = X1 * Z2Z2 % n
    U2 = X2 * Z1Z1 % n
    S1 = Y1 * Z2 * Z2Z2 % n
    S2 = Y2 * Z1 * Z1Z1 % n
    if U1 == U2:
        assert gcd(Z1 * Z2 % n, n) == 1, "degenerate Z in jac_add"
        if (S1 + S2) % n == 0:
            if (S1 - S2) % n != 0:
                assert gcd((S1 - S2) % n, n) == 1, "nontrivial gcd(S1 - S2, n)"
            return (mpz(1), mpz(1), mpz(0))
        assert (S1 - S2) % n == 0, "ambiguous equal-x branch (S1 != +-S2 mod n)"
        return jac_dbl(X1, Y1, Z1, a, n)
    H = (U2 - U1) % n
    Z3 = Z1 * Z2 * H % n
    assert gcd(Z3, n) == 1, "nontrivial gcd(Z1*Z2*(U2 - U1), n) in jac_add"
    R = (S2 - S1) % n
    HH = H * H % n
    HHH = H * HH % n
    V = U1 * HH % n
    X3 = (R * R - HHH - 2 * V) % n
    Y3 = (R * (V - X3) - S1 * HHH) % n
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
    assert t * t <= 4 * N, "Hasse violated"
    m = N + 1 - t
    assert s > 0 and m % s == 0
    q = m // s
    D = q * q + 6 * q + 1 - N
    assert q > 1 and D > 0 and D * D > 16 * q * (q + 1) * (q + 1), "q too small for Goldwasser-Kilian"
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
    with open(sys.argv[2], "r", encoding="utf-8") as fh:
        expected_txt = fh.read()
    assert _INT_TEXT_RE.fullmatch(expected_txt), (
        "invalid integer in expected candidate file")
    expected = mpz(expected_txt.strip())
    assert isinstance(cert, list) and len(cert) > 0, "empty certificate"
    assert (isinstance(cert[0], list) and len(cert[0]) == 5
            and not isinstance(cert[0][0], list)), "malformed step 0 in certificate"
    assert mpz(cert[0][0]) == expected, (
        "BINDING FAILURE: certificate top-level candidate != expected")
    current = expected
    for i, step in enumerate(cert):
        assert isinstance(step, list) and len(step) == 5, f"malformed step {i}"
        N, t, s, a4, pt = step
        assert isinstance(pt, list) and len(pt) == 2, f"malformed point at step {i}"
        x, y = pt
        for val in (N, t, s, a4, x, y):
            assert not isinstance(val, list), f"unexpected nested list at step {i}"
        assert mpz(N) == current, f"chain broken at step {i}"
        current = verify_step(mpz(N), mpz(t), mpz(s), mpz(a4),
                              mpz(x), mpz(y))
        if i % 50 == 0:
            print(f"  step {i}: {len(str(N))} digits ok", flush=True)
    assert current < 2 ** 64, f"final q has {len(str(current))} digits"
    assert gmpy2.is_prime(int(current)), "final small prime fails BPSW"
    print(f"chain length {len(cert)}, final prime {current}")
    print("INDEPENDENT ECPP CHECK PASSED")


if __name__ == "__main__":
    main()

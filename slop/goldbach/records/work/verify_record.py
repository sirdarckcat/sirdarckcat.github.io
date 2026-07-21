#!/usr/bin/env python3
"""Standalone verifier for a certified Goldbach-gap record.

Requires ONLY Python 3 standard library (gmpy2 is used to accelerate if
present, but the proof path is identical without it).

Input: a JSON package
{
  "N": "<decimal>",             # the even integer
  "q": <int>,                   # claimed least Goldbach summand  g(N) = q
  "classes": [[r, b], ...],     # prime moduli & residues: N ≡ b (mod r)
  "t": <int>,                   # N = CRT(classes ∪ {N≡0 mod 2}) + t * M
  "ecpp_cert": [...],           # PARI-style ECPP certificate for N - q
  "claims": {...}               # record claims to check (see below)
}

Checks performed (all must pass):
 A. N reconstructs exactly from the congruence system + t; N is even.
 B. Every prime p < q has N - p composite:
    - p = 2: N - 2 is even and > 2;
    - covered p (p ≡ b mod r for a used class): verifies N ≡ b (mod r),
      hence r | N - p with 1 < r < N - p  => proper divisor;
    - residual p: strong-probable-prime test base 2 (and base 3) must FAIL:
      a failure is a one-sided *proof* of compositeness.
 C. q is prime (trial division), and N - q is prime via the ECPP certificate
    (independently re-verified here, chain terminating below 2^64 with
    deterministic Miller-Rabin on the verified base set).
 D. The claimed record inequalities hold exactly (no rounding):
    claims may contain: {"q_exceeds": X}  => q > X
                        {"N_below": "<decimal>"} => N < that integer
                        {"digits_at_most": D} => len(dec(N)) <= D
Exit code 0 iff everything passes.
"""
import hashlib, json, math, sys

# ---------------------------------------------------------------- utilities
def sieve_flags(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(range(i * i, n + 1, i)))
    return s

def sprp_composite(n, a):
    """True iff a proves n composite by the strong probable-prime test.
    (Primes NEVER return True: this is a rigorous compositeness witness.)"""
    if n % 2 == 0: return n != 2
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1: return False
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1: return False
    return True

# ------------------------------------------------- ECPP certificate checker
class CompositeFactor(Exception): pass

def egcd(a, b):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        qt, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - qt * x1
        y0, y1 = y1, y0 - qt * y1
    return a, x0, y0

def inv_mod(z, n):
    g, x, _ = egcd(z % n, n)
    if g != 1: raise CompositeFactor(g)
    return x % n

def ec_add(P, Qp, a, n):
    if P is None: return Qp
    if Qp is None: return P
    x1, y1 = P; x2, y2 = Qp
    if (x1 - x2) % n == 0:
        if (y1 + y2) % n == 0: return None
        lam = (3 * x1 * x1 + a) * inv_mod(2 * y1, n) % n
    else:
        lam = (y2 - y1) * inv_mod(x2 - x1, n) % n
    x3 = (lam * lam - x1 - x2) % n
    return (x3, (lam * (x1 - x3) - y1) % n)

def ec_mul(k, P, a, n):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a, n)
        P = ec_add(P, P, a, n)
        k >>= 1
    return R

def is_prime_u64(n):
    assert 1 < n < 3317044064679887385961981
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    return not any(sprp_composite(n, a) for a in (2,3,5,7,11,13,17,19,23,29,31,37,41))

def ecpp_verify(cert, expect_top):
    cert = [[int(v) if not isinstance(v, list) else [int(w) for w in v] for v in st] for st in cert]
    assert cert[0][0] == expect_top, "certificate is not for the claimed integer"
    for idx, (N, t, s, a, (x, y)) in enumerate(cert):
        assert N > 1 and math.gcd(N, 6) == 1, f"step {idx}: gcd(N,6)!=1"
        m = N + 1 - t
        assert s > 0 and m % s == 0, f"step {idx}: s ∤ m"
        assert t * t <= 4 * N, f"step {idx}: Hasse bound violated"
        q = m // s
        r4 = math.isqrt(math.isqrt(N))
        while (r4 + 1) ** 4 <= N: r4 += 1
        assert q > (r4 + 1) ** 2, f"step {idx}: q <= (N^(1/4)+1)^2"
        b = (y * y - x * x * x - a * x) % N
        assert math.gcd((4 * a * a * a + 27 * b * b) % N, N) == 1, f"step {idx}: singular curve"
        try:
            R = ec_mul(s, (x % N, y % N), a, N)
            assert R is not None, f"step {idx}: [s]P = O"
            assert ec_mul(q, R, a, N) is None, f"step {idx}: [q][s]P != O"
        except CompositeFactor as e:
            raise AssertionError(f"step {idx}: nontrivial gcd {e.args[0]} => N composite")
        if idx + 1 < len(cert):
            assert cert[idx + 1][0] == q, f"step {idx}: chain broken"
        else:
            assert is_prime_u64(q), f"final step: q={q} not proven prime"
    return True

# ------------------------------------------------------------------- driver
def main(path):
    try:
        import gmpy2
        fast_comp = lambda n: not gmpy2.is_strong_prp(n, 2) or not gmpy2.is_strong_prp(n, 3)
        print("[info] gmpy2 acceleration available")
    except ImportError:
        fast_comp = None
        print("[info] pure stdlib mode")
    pkg = json.load(open(path))
    N = int(pkg["N"]); q = int(pkg["q"]); t = int(pkg["t"])
    classes = [(int(r), int(b)) for r, b in pkg["classes"]]
    claims = pkg.get("claims", {})
    print(f"[input] sha256 of package file: {hashlib.sha256(open(path,'rb').read()).hexdigest()}")

    # A. reconstruct N by CRT
    assert len(set(r for r, _ in classes)) == len(classes), "duplicate modulus"
    M, N0 = 2, 0                                    # start with N ≡ 0 (mod 2)
    for r, b in sorted(classes):
        assert all(r % pp for pp in range(2, math.isqrt(r) + 1)), f"modulus {r} not prime"
        assert 0 <= b < r, f"bad residue {b} mod {r}"
        g, inv, _ = egcd(M % r, r)
        assert g == 1, "moduli not coprime"
        N0 = N0 + M * ((b - N0) * inv % r)
        M *= r
    N0 %= M
    assert N == N0 + t * M, "N does not reconstruct from congruences + t"
    assert N % 2 == 0, "N not even"
    print(f"[A] N reconstructed: {len(str(N))} digits, t={t}, {len(classes)} congruences OK")

    # B. all primes p < q have composite complement
    for r, b in classes:
        assert N % r == b, f"N !≡ {b} (mod {r})"
        assert 1 < r < N - q, "witness would not be a proper divisor"
    flags = sieve_flags(q)                          # primes < q  (q excluded below)
    covered = bytearray(q)                          # mark covered primes
    for r, b in classes:
        start = b if b > 0 else r
        for x in range(start, q, r):
            covered[x] = 1
    residual = [p for p in range(3, q, 2) if flags[p] and not covered[p]]
    n_primes = sum(1 for p in range(2, q) if flags[p])
    print(f"[B] primes below q: {n_primes}; residual (uncovered): {len(residual)}")
    assert (N - 2) % 2 == 0 and N - 2 > 2           # p = 2
    for i, p in enumerate(residual):
        c = N - p
        if fast_comp is not None:
            assert fast_comp(c), f"N - {p} is a probable prime! g(N) claim false"
        else:
            assert sprp_composite(c, 2) or sprp_composite(c, 3), \
                f"N - {p} passed SPRP(2,3): cannot certify composite"
        if (i + 1) % 500 == 0:
            print(f"    ... {i+1}/{len(residual)} residual complements proven composite", flush=True)
    print(f"[B] all {len(residual)} residual complements composite; "
          f"all covered complements divisible by their class modulus")

    # C. the partition N = q + (N - q)
    assert flags[q] if q < len(flags) else all(q % d for d in range(2, math.isqrt(q) + 1)), "q not prime"
    assert all(q % d for d in range(2, math.isqrt(q) + 1)) and q > 1, "q not prime"
    ecpp_verify(pkg["ecpp_cert"], N - q)
    print(f"[C] q = {q} prime (trial division); N - q proven prime by ECPP "
          f"({len(pkg['ecpp_cert'])} steps, independently re-verified)")

    # D. record claims
    if "q_exceeds" in claims:
        assert q > int(claims["q_exceeds"]), "q does not exceed claimed bound"
        print(f"[D] q = {q} > {claims['q_exceeds']} OK")
    if "N_below" in claims:
        assert N < int(claims["N_below"]), "N not below claimed bound"
        print(f"[D] N < N_bound OK ({len(str(N))} vs {len(str(int(claims['N_below'])))} digits)")
    if "digits_at_most" in claims:
        assert len(str(N)) <= int(claims["digits_at_most"]), "too many digits"
        print(f"[D] N has {len(str(N))} <= {claims['digits_at_most']} digits OK")
    print(f"[PASS] g(N) = {q} for the {len(str(N))}-digit N in {path}")

if __name__ == "__main__":
    main(sys.argv[1])

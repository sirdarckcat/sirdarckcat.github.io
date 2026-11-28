#!/usr/bin/env python3
"""Pratt certificates for the primes N - g of the frontier's numbers, as data for a kernel check.

    python3 frontier_pratt.py N g [N g ...]  > frontier_pratt.json

For a prime n the certificate is {"n", "a", "factors"}: the distinct primes q dividing n - 1, each with its own
certificate unless q < 1000, and a base a with a^(n-1) = 1 and a^((n-1)/q) != 1 (mod n) for every q.  The script
checks every certificate it writes with plain modular exponentiation before printing.
"""
import sys, json, sympy
def pratt(n):
    n = int(n)
    if n < 1000:
        assert sympy.isprime(n); return {"n": str(n)}
    f = sorted(sympy.factorint(n - 1))
    for a in range(2, 1000):
        if pow(a, n - 1, n) == 1 and all(pow(a, (n - 1) // q, n) != 1 for q in f):
            return {"n": str(n), "a": a, "factors": [pratt(q) for q in f]}
    raise SystemExit(f"no base found for {n}")
def verify(c):
    n = int(c["n"])
    if "a" not in c:
        assert n < 1000 and all(n % d for d in range(2, int(n ** .5) + 1)) and n > 1; return n
    qs = [verify(x) for x in c["factors"]]; m = n - 1
    for q in qs:
        assert m % q == 0
        while m % q == 0: m //= q
    assert m == 1 and pow(c["a"], n - 1, n) == 1 and all(pow(c["a"], (n - 1) // q, n) != 1 for q in qs)
    return n
out = []
for N, g in zip(sys.argv[1::2], sys.argv[2::2]):
    N, g = int(N), int(g); c = pratt(N - g); assert verify(c) == N - g
    out.append({"N": str(N), "digits": len(str(N)), "g": g, "N_minus_g": str(N - g), "pratt": c})
print(json.dumps(out, indent=1))

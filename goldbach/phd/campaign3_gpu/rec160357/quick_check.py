# Quick independent check of the g = 160,357 near-miss: N from the spec, then BPSW on N - p for every prime p < g and on N - g.
import json, sys, time
import gmpy2
from gmpy2 import mpz
f = json.load(open(sys.argv[1])); s = json.load(open(sys.argv[2]))[0]
N0, M, k, g = mpz(s["N0"]), mpz(s["M"]), int(f["k"]), int(f["g"])
N = N0 + k * M
print("N from spec equals the logged N:", N == mpz(f["N"]), "| even:", N % 2 == 0, "| digits:", len(str(N)), "| N < 10^200:", N < mpz(10) ** 200, "| N >= 10^199:", N >= mpz(10) ** 199)
t0 = time.time(); p = 2; first = None; n = 0
while p < g:
    n += 1
    if gmpy2.is_bpsw_prp(N - p):
        first = p; break
    p = int(gmpy2.next_prime(p))
print(f"primes p < {g} checked: {n}; first p with N - p a BPSW probable prime: {first} ({time.time() - t0:.1f} s)")
print("N - g is a BPSW probable prime:", gmpy2.is_bpsw_prp(N - g), "| g prime:", gmpy2.is_prime(g))
print("QUICK-CHECK", "PASSED: g(N) =", g if first is None and gmpy2.is_bpsw_prp(N - g) and N == mpz(f["N"]) else "FAILED")

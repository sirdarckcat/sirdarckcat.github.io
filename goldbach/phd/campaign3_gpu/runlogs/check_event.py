# Independent CPU check of a near-miss event line: N even, 200 digits, N < 10^200, N - p composite for every prime p < g (gmpy2 is_prime, 25 rounds), N - g a probable prime.
import json, sys, time
import gmpy2
r = json.loads(open(sys.argv[1]).readline())
N, g = gmpy2.mpz(r["N"]), int(r["g"])
t = time.time()
assert N % 2 == 0 and len(str(N)) == 200 and N < gmpy2.mpz(10) ** 200, "shape"
assert gmpy2.is_prime(g), "g prime"
p, n = 2, 0
while p < g:
    assert not gmpy2.is_prime(N - p, 25), "N - %d is a probable prime" % p
    n += 1
    p = int(gmpy2.next_prime(p))
assert gmpy2.is_prime(N - g, 25), "N - g composite"
print("CHECK PASSED: g(N) = %d, %d primes below g all give composite N - p, N - g is a probable prime; N = %.4e; %.1f s" % (g, n, float(N), time.time() - t))

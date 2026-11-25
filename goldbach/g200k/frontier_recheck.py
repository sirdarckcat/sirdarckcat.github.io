"""Independent recheck of frontier hits from N alone: every N - p (p prime < g) composite by sympy's BPSW (a False is a witness),
N - g a BPSW probable prime and a 50-round Miller-Rabin probable prime (gmpy2), closeness from goldbach/closeness.py."""
import json, sys
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach")
import gmpy2, sympy, closeness
from sympy import primerange
r = json.load(open(sys.argv[1]))                                   # a frontier.py output
ok_all = True
for h in sorted(r["hits"], key=lambda h: -h["closeness"]):
    N = int(h["N"]); g = h["g"]
    assert N % 2 == 0 and str(N) == h["N"]
    comp = all(not sympy.isprime(N - p) for p in primerange(2, g))
    prime = sympy.isprime(N - g) and gmpy2.is_prime(N - g, 50)
    c = g / closeness.ceiling(closeness.ln_int(N))
    ok = comp and prime and abs(c - h["closeness"]) < 1e-12 and len(str(N)) == h["digits"]
    ok_all &= ok
    print(f"{len(str(N))} digits, g = {g}, closeness {c:.4f}: all N - p composite for p < g: {comp}; N - g prime (BPSW + MR50): {prime}; {'OK' if ok else 'FAIL'}", flush=True)
print("ALL OK" if ok_all else "SOME FAILED")

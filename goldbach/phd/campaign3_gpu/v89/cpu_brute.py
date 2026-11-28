#!/usr/bin/env python3
"""CPU brute force for the known case (independent of the GPU path): for the members k in [k_lo, k_lo + n) of a vector (k_lo the first 200-digit k), the
least prime q with N - q prime, N = N0 + k M.  Covered rows are recomputed here from N0 and M alone (q is covered exactly when gcd(N0 - q, M) > 1; then
N - q, which has the same residues mod the moduli, has a factor r <= 463 and is composite); the other primes q < Q are scanned in ascending order with a
BPSW test (gmpy2.is_bpsw_prp) until the first prime.  Prints every member whose least prime q is >= T (and those with none below Q).
    python3 cpu_brute.py specs.json T n [procs]"""
import json, math, sys
from multiprocessing import Pool
import gmpy2
from gmpy2 import mpz

def primes_below(n):
    s = bytearray([1]) * n; s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(2, n) if s[i]]

spec = json.load(open(sys.argv[1]))[0]
T, n = int(sys.argv[2]), int(sys.argv[3])
procs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
N0, M, Q = int(spec["N0"]), int(spec["M"]), int(spec["Q"])
k_lo = -(-(10 ** 199 - N0) // M)
P = primes_below(Q)
resid = [q for q in P if q > 2 and math.gcd(N0 - q, M) == 1]     # q = 2: N - 2 is even
N0m, Mm = mpz(N0), mpz(M)

def scan(k0):
    out = []
    for k in range(k0, min(k0 + 4096, k_lo + n)):
        N = N0m + k * Mm
        first = None
        for q in resid:
            if gmpy2.is_bpsw_prp(N - q):
                first = q
                break
        if first is None or first >= T:
            out.append((k, first))
    return out

if __name__ == "__main__":
    print(f"{spec['name']}: residual recomputed from gcd: {len(resid)} rows ({'identical to' if resid == [int(q) for q in spec['residual']] else 'DIFFERENT from'} the spec's), k in [{k_lo}, {k_lo + n}), T = {T}", flush=True)
    with Pool(procs) as pool:
        res = [x for part in pool.map(scan, range(k_lo, k_lo + n, 4096)) for x in part]
    for k, q in sorted(res):
        print(f"BRUTE k={k} q={q}")
    print(f"BRUTE-DONE {len(res)} members with no prime below {T}")

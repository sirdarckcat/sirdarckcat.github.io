# T5: check a hit from N alone. For every odd prime q < Q: N - q is shown composite, by a factor (trial division by the primes up
# to F) or, when no factor is found, by a failed base-2 Fermat test (a proof of compositeness). Then g(N) = the least prime p with
# N - p prime: the primes p >= Q in increasing order, N - p tested with gmpy2.is_prime (BPSW plus Miller-Rabin rounds).
#   python3 verify.py N_file_or_hit.json [Q] [F]      -> prints and writes verify_<digits>digit.json
import sys, json, time
import numpy as np
import gmpy2
from gmpy2 import mpz, powmod

def primes_below(n):
    s = np.ones(n, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

if __name__ == "__main__":
    src = sys.argv[1]; Q = int(sys.argv[2]) if len(sys.argv) > 2 else 1000003; F = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
    txt = open(src).read().strip()
    N = mpz(json.loads(txt)["N"]) if txt.startswith("{") else mpz(txt)
    assert N % 2 == 0, "N must be even"
    digits = len(str(N)); t0 = time.time()
    P = primes_below(max(Q, F) + 1); rows = P[(P > 2) & (P < Q)]; small = P[P <= F]
    # N mod each small prime, once; then N - q is divisible by s iff q = N (mod s)
    Nmod = np.array([int(N % int(s)) for s in small], dtype=np.int64)
    factor = np.zeros(len(rows), np.int64)
    for s, r in zip(small.tolist(), Nmod.tolist()):
        m = (rows % s == r) & (factor == 0)                    # rows q with s | N - q (N - q > s, so composite)
        factor[m] = s
    nf = int((factor > 0).sum()); fermat = 0; bad = []
    for q in rows[factor == 0].tolist():
        m = N - q
        if powmod(2, m - 1, m) == 1: bad.append(q)
        else: fermat += 1
    ok = not bad
    print(f"N has {digits} digits; {len(rows):,} odd primes q < {Q:,}: {nf:,} with a factor <= {F:,} of N - q, {fermat:,} by a failed Fermat test; "
          f"{len(bad)} not shown composite ({time.time() - t0:.0f} s)", flush=True)
    g = None
    if ok:
        p = gmpy2.next_prime(Q - 1)
        while True:
            if gmpy2.is_prime(N - p, 25): g = int(p); break
            p = gmpy2.next_prime(p)
        print(f"g(N) = {g:,}: N - {g} is a probable prime (BPSW + 25 rounds); every q below it fails ({time.time() - t0:.0f} s)")
    json.dump(dict(N=str(N), digits=digits, Q=Q, rows=len(rows), by_factor=nf, by_fermat=fermat, not_shown=bad[:20], g=g), open(f"verify_{digits}digit.json", "w"))

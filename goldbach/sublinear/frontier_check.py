#!/usr/bin/env python3
"""Recompute g(N) from N alone, with proofs on both sides, and its closeness (for the frontier's numbers of up to some 60 digits).

    python3 frontier_check.py N [N ...]

g(N) is the least prime p with N - p prime.  For every odd prime p below g the number N - p is shown composite by a
witness (a base-2 or base-3 Fermat test that fails, or a factor up to 13); N - g is proved prime by a Lucas n - 1 proof:
n - 1 is factored completely (sympy), each prime factor is proved in the same way or lies below 2^64 (where sympy's test
is deterministic), and a base a is found with a^(n-1) = 1 and a^((n-1)/q) != 1 (mod n) for every prime factor q.
Above 10^40, where factoring n - 1 may not finish, N - g is proved prime with PARI instead when the module cypari2 can
be imported: an ECPP certificate (primecert) that PARI then validates (primecertisvalid).  Without it the line says
"probable prime (25 rounds)" and the upper side is not a proof.
Shares nothing with the scanners (../fscan, ../sieve200) or with ../fscan/check.py.  Needs gmpy2 and sympy.
"""
import sys, math
import gmpy2, sympy
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), ".."))
import closeness

def lucas_proof(n):
    n = int(n)
    if n < 2 ** 64: return sympy.isprime(n)
    f = sympy.factorint(n - 1)
    if not all(lucas_proof(q) for q in f): return False
    for a in range(2, 200):
        if pow(a, n - 1, n) != 1: return False
        if all(pow(a, (n - 1) // q, n) != 1 for q in f): return True
    return False

def prove(m):
    """(is prime, how it was proved)"""
    if m < 10 ** 40: return lucas_proof(m), "N - g proved prime (n - 1)"
    if not gmpy2.is_prime(m, 25): return False, ""
    try:
        import cypari2
        pari = cypari2.Pari(); pari.allocatemem(2 * 10 ** 9, silent=True)
        c = pari.primecert(m)
        return bool(pari.primecertisvalid(c)), "N - g proved prime (ECPP certificate, validated by PARI)"
    except ImportError:
        return True, "N - g a probable prime (25 rounds), not proved"

def check(N):
    assert N % 2 == 0 and N > 10 ** 6
    p = 2; ncomp = 0
    while True:
        p = int(gmpy2.next_prime(p)); m = N - p
        if pow(2, m - 1, m) != 1 or pow(3, m - 1, m) != 1 or any(m % r == 0 for r in (3, 5, 7, 11, 13)): ncomp += 1; continue
        ok, how = prove(m)
        if ok: return p, ncomp, how
        # passes both Fermat tests and is not proved prime: it must then be shown composite some other way
        assert not gmpy2.is_strong_prp(m, 2) or not gmpy2.is_strong_prp(m, 5), f"undecided: N - {p}"
        ncomp += 1

if __name__ == "__main__":
    for s in sys.argv[1:]:
        N = int(s); g, ncomp, how = check(N); c = closeness.ceiling(math.log(N))
        print(f"N = {N} | digits {len(str(N))} | g = {g} | odd primes below g, all with N - p composite by a witness: {ncomp} | {how} | ceiling {c:.0f} | closeness {100 * g / c:.2f}%")

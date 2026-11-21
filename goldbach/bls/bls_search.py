#!/usr/bin/env python3
"""Game 1 without ECPP: a full cover plus a complement proven prime by BLS.

Construction. Take the full cover {N = a_r (mod r)} of every odd prime q < Q
(full_cover.py) and let g be the least prime >= Q that the cover misses.
Add the 2-adic condition N = g + 1 + 2^n (mod 2^(n+1)). It is compatible
with the cover by CRT, because the cover modulus is odd. Then
P = N - g = 1 + 2^n * R with R odd, and N runs over the progression
N_i = N_0 + i*L, where L = 2^(n+1) * prod(r).

Proof of g(N) = g.
  * Every odd prime q < g is in some class a_r (mod r), so r | N - q < N
    and N - q is composite. N is even, so N - 2 is composite.
  * P = N - g is prime, by Brillhart-Lehmer-Selfridge with F = 2^n and
    F^3 > P. Find a with a^((P-1)/2) = -1 (mod P). By Pocklington, every
    prime p | P then has p = 1 (mod F). If P were composite it would be
    (uF+1)(vF+1) with uv < F and u+v < F. Its base-F digits would be
    c2 = uv and c1 = u+v, so c1^2 - 4*c2 = (u-v)^2 would be a square. So
    when c1^2 - 4*c2 is not a square, P is prime. Cost: one modexp.

    python3 goldbach/bls/bls_search.py 1200000 --out goldbach/bls/rec.json
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import gmpy2
import numpy as np
from gmpy2 import mpz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from full_cover import build, primes_upto  # noqa: E402


def crt(pairs):
    x, m = mpz(0), mpz(1)
    for r, a in pairs:
        r = mpz(r)
        t = ((mpz(a) - x) * gmpy2.invert(m % r, r)) % r
        x += m * t
        m *= r
    return x, m


def least_uncovered_prime(Q, cover):
    rs = np.array([r for r, _ in cover], dtype=np.int64)
    as_ = np.array([a for _, a in cover], dtype=np.int64)
    p = int(gmpy2.next_prime(Q - 1))
    while True:
        if not np.any(p % rs == as_):
            return p
        p = int(gmpy2.next_prime(p))


def sieve_offsets(P0, L, I, lo, S, log):
    """alive[i] False when P0 + i*L has a prime factor p in (lo, S]."""
    alive = np.ones(I, dtype=bool)
    ps = primes_upto(S)
    ps = ps[ps > lo]
    t0 = time.time()
    big_roots = []
    for p in ps.tolist():
        Lp = int(L % p)
        root = (-int(P0 % p)) * pow(Lp, -1, p) % p
        if p < I:
            alive[root::p] = False
        elif root < I:
            big_roots.append(root)
    if big_roots:
        alive[np.array(big_roots, dtype=np.int64)] = False
    log(f"sieve: {ps.size:,} primes in ({lo}, {S:,}], {alive.sum():,}/{I:,}"
        f" offsets survive, {time.time() - t0:.1f}s")
    return alive


_P0 = _L = None


def _init(p0s, ls):
    global _P0, _L
    _P0, _L = mpz(p0s, 16), mpz(ls, 16)


def _test(i):
    P = _P0 + i * _L
    a = 3
    while gmpy2.jacobi(a, P) != -1:
        a = int(gmpy2.next_prime(a))
    x = gmpy2.powmod(a, (P - 1) >> 1, P)
    return i, a, bool(x == P - 1)


def bls_square_check(P, n):
    F = mpz(1) << n
    R = (P - 1) // F
    assert (P - 1) % F == 0 and R % 2 == 1
    assert F ** 3 > P >= F ** 2
    c2, c1 = divmod(R, F)
    D = c1 * c1 - 4 * c2
    return D < 0 or not gmpy2.is_square(D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("Q", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--offsets", type=int, default=300_000)
    ap.add_argument("--sieve", type=int, default=100_000_000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--log")
    a = ap.parse_args()

    logf = open(a.log, "a") if a.log else None

    def log(msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        if logf:
            logf.write(line + "\n")
            logf.flush()

    t_start = time.time()
    cover, ntarget = build(a.Q)
    r_max = cover[-1][0]
    g = least_uncovered_prime(a.Q, cover)
    M = mpz(1)
    for r, _ in cover:
        M *= r
    I = a.offsets
    # F = 2^n with F^3 > P for every tested P < (I+1) * 2^(n+1) * M
    n = (int(M.bit_length()) + (I + 1).bit_length() + 1) // 2 + 2
    pairs = [(1 << (n + 1), g + 1 + (1 << n))] + cover
    N0, L = crt(pairs)
    P0 = (N0 - g) % L
    log(f"Q={a.Q:,} cover: {len(cover) + 1} congruences, r_max={r_max}, "
        f"M {len(str(M))} digits; g={g:,}; n={n}; P ~ "
        f"{int((P0 + L).bit_length() * math.log10(2))} digits; "
        f"cover+CRT {time.time() - t_start:.1f}s")

    alive = sieve_offsets(P0, L, I, r_max, a.sieve, log)
    cand = np.nonzero(alive)[0].tolist()
    lnP = float(gmpy2.log(P0 + L))
    exp_tests = lnP / (math.exp(0.5772156649) * math.log(a.sieve))
    log(f"expected BLS tests ~ {exp_tests:.0f} (lnP / e^gamma ln S)")

    found = None
    t0 = time.time()
    init_args = (P0.digits(16), L.digits(16))
    _init(*init_args)  # fail fast here, not in a Pool respawn loop
    assert _P0 == P0 and _L == L
    with Pool(a.workers, initializer=_init, initargs=init_args) as pool:
        for k, (i, base, ok) in enumerate(pool.imap(_test, cand,
                                                    chunksize=1), 1):
            if k % 25 == 0:
                el = time.time() - t0
                log(f"tests {k:,}  elapsed {el / 60:.1f} min  "
                    f"({el / k:.2f}s/test wall)")
            if ok:
                P = P0 + i * L
                if bls_square_check(P, n):
                    found = (i, base, k)
                    break
                log(f"i={i}: Euler -1 but BLS square case; continuing")
        pool.terminate()
    if not found:
        log("no prime in range; widen --offsets")
        sys.exit(1)
    i, base, k = found
    P = P0 + i * L
    N = P + g
    rec = {
        "game": "Game 1 (largest g), BLS-certified complement",
        "Q": a.Q, "g": g, "n": n, "i": i, "bls_base": base,
        "digits_N": len(N.digits()), "digits_P": len(P.digits()),
        "congruences": len(cover) + 1, "r_max": r_max,
        "two_adic": [n + 1, int(g + 1 + (1 << n))],
        "cover": cover, "N": N.digits(),
        "search": {"tests": k, "minutes": round((time.time() - t0) / 60, 2),
                   "expected_tests": round(exp_tests), "sieve": a.sieve,
                   "workers": a.workers},
    }
    with open(a.out, "w") as fh:
        json.dump(rec, fh)
    log(f"FOUND i={i} after {k} tests: g(N) = {g:,}, N has "
        f"{rec['digits_N']:,} digits; wrote {a.out}")


if __name__ == "__main__":
    main()

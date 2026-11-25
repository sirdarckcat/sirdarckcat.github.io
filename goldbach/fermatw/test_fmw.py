#!/usr/bin/env python3
"""fmw against Python pow: residues y = 2^(1-n) mod n (y < 4n, reduced here) and verdicts, for random odd numbers of the
sizes each L serves, mixed lengths in one batch, primes, base-2 pseudoprimes; the member scheduler against a plain loop.
    python3 test_fmw.py [L ...]        (default: 20 21 23 26)"""
import random
import sys
import time

import numpy as np
import gmpy2
import fmw

Ls = [int(a) for a in sys.argv[1:]] or [20, 21, 23, 26]
rng = random.Random(12345)


def check(ns, L):
    vd, ys = fmw.test(ns, L, want_y=True)
    for n, v, y in zip(ns, vd, ys):
        ref = pow(2, n - 1, n) == 1
        assert y < 4 * n, (n, y)
        assert y % n == pow(2, 1 - n, n), (L, n.bit_length())
        assert bool(v) == ref, (L, n.bit_length(), n, v, ref)


for L in Ls:
    t0 = time.time()
    mb = 52 * L - 12
    # random odd numbers at the top size and mixed sizes
    ns = [rng.getrandbits(mb) | (1 << (mb - 1)) | 1 for _ in range(64)]
    check(ns, L)
    ns = [rng.getrandbits(rng.randint(max(8, mb - 300), mb)) | 1 for _ in range(64)]
    ns = [n for n in ns if n > 3]
    check(ns, L)
    # primes near the top size and mixed
    ps = [int(gmpy2.next_prime(rng.getrandbits(mb - 1) | (1 << (mb - 2)))) for _ in range(24)]
    ps += [int(gmpy2.next_prime(rng.getrandbits(rng.randint(max(8, mb - 200), mb - 1)))) for _ in range(16)]
    vd = fmw.test(ps, L)
    assert vd.all(), (L, vd)
    # base-2 pseudoprimes: (2^p - 1) for prime p is a base-2 psp when composite? use products of primes p with 2^(n-1)=1:
    # n = (2^k+1)... use the classical Cipolla construction: n = (4^p - 1)/3 for prime p > 3 is a base-2 psp
    psp = []
    for p in (331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503):
        n = (4 ** p - 1) // 3
        if n.bit_length() <= mb and not gmpy2.is_prime(n):
            psp.append(n)
    if psp:
        assert all(pow(2, n - 1, n) == 1 for n in psp)
        vd = fmw.test(psp, L)
        assert vd.all(), (L, "psp", vd)
    # composites that are products of two primes (should fail)
    cs = [int(gmpy2.next_prime(rng.getrandbits(mb // 2))) * int(gmpy2.next_prime(rng.getrandbits(mb // 2 - 2))) for _ in range(16)]
    vd = fmw.test(cs, L)
    assert not vd.any()
    # member scheduler against a plain loop
    h = fmw.lib(L)
    M = int(gmpy2.primorial(500)) * 2
    while M.bit_length() > mb - 40:
        M //= 3
    N0 = rng.getrandbits(M.bit_length() - 1) * 2
    U = [int(q) for q in range(3, 20000) if gmpy2.is_prime(q)]
    mem = fmw.Members(N0, M, U, 1 << 20)
    assert mem.L == fmw.limbs_for((N0 + (1 << 20) * M).bit_length())
    kv = np.array([rng.randrange(1 << 20) for _ in range(40)], dtype=np.uint64)
    rows, offs = [], [0]
    for k in kv:
        r = sorted(rng.sample(range(len(U)), rng.randint(0, 60)))
        rows += r
        offs.append(len(rows))
    rows = np.array(rows, dtype=np.uint16)
    offs = np.array(offs, dtype=np.int64)
    fp = mem.first_pass(kv, rows, offs)
    for t, k in enumerate(kv):
        want = -1
        for pos, r in enumerate(rows[offs[t]:offs[t + 1]]):
            n = N0 + int(k) * M - U[r]
            if pow(2, n - 1, n) == 1:
                want = pos
                break
        assert fp[t] == want, (t, fp[t], want)
    print(f"L={L}: ok ({len(psp)} psp) {time.time() - t0:.1f}s", flush=True)
print("all ok")

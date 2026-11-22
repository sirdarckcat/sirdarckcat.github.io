#!/usr/bin/env python3
"""fm13 against Python's pow: the final residue y = 2^(1-n) mod n of every lane, and the verdicts, on random numbers of
many bit lengths, primes, pseudoprimes, and the campaign3-sized numbers.

    python3 test_fm13.py [--lib libfm13.so] [--count 2000]
"""
import argparse
import ctypes
import os
import random
import sys

import numpy as np
import gmpy2

HERE = os.path.dirname(os.path.abspath(__file__))
NW = 11


def to_words(x):
    return np.frombuffer(int(x).to_bytes(8 * NW, "little"), dtype=np.uint64)


def from_words(w):
    return int.from_bytes(np.ascontiguousarray(w).tobytes(), "little")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", default=None, help="default: the library fm13.py builds")
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    if a.lib is None:
        sys.path.insert(0, HERE)
        import fm13
        a.lib = fm13.build()
    lib = ctypes.CDLL(a.lib)
    lib.fm13_test.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    lib.fm13_lanes.restype = ctypes.c_int
    lanes = lib.fm13_lanes()
    rng = random.Random(a.seed)
    ok = True

    def check(name, ns):
        nonlocal ok
        cnt = len(ns)
        nw = np.stack([to_words(n) for n in ns])
        y = np.zeros((cnt, NW), dtype=np.uint64)
        v = np.zeros(cnt, dtype=np.uint8)
        lib.fm13_test(cnt, nw.ctypes.data, v.ctypes.data, y.ctypes.data)
        bad_y = bad_v = 0
        for i, n in enumerate(ns):
            yy = from_words(y[i])
            if yy >= 4 * n or yy % n != pow(2, -(n - 1), n):
                bad_y += 1
            if bool(v[i]) != (pow(2, n - 1, n) == 1):
                bad_v += 1
        pos = int(v.sum())
        print(f"  {name:<44s} {cnt:5d} numbers  positives {pos:4d}   wrong residues {bad_y}   wrong verdicts {bad_v}", flush=True)
        ok &= bad_y == 0 and bad_v == 0

    def rnd(bits):
        return rng.getrandbits(bits) | (1 << (bits - 1)) | 1

    print("lanes per batch:", lanes)
    for bits in (661, 664, 660, 650, 640, 600, 500, 300, 200, 100):
        check(f"random odd, {bits} bits", [rnd(bits) for _ in range(min(a.count, 300))])
    check("mixed 655..664 bits in one call", [rnd(rng.randint(655, 664)) for _ in range(a.count)])
    check("batch sizes 1..40, 661 bits", [rnd(661) for _ in range(1)] + [rnd(661) for _ in range(39)])
    for cnt in (1, 2, 7, 8, 9, 15, 16, 17, 31, 33):
        check(f"count {cnt}", [rnd(662) for _ in range(cnt)])
    pr = [int(gmpy2.next_prime(gmpy2.mpz(rnd(661)))) for _ in range(120)]
    check("primes, 661 bits", pr)
    pr2 = [int(gmpy2.next_prime(gmpy2.mpz(rnd(rng.randint(500, 664))))) for _ in range(120)]
    check("primes, 500-664 bits", pr2)
    # Fermat base-2 pseudoprimes of different sizes: products of two primes p, q with 2^(n-1) = 1 mod n are rare; use Carmichael-like
    # constructions: n = p q with q = 2 (p-1) + 1 style is not guaranteed, so build n = p * (k (p-1) + 1) and keep those that pass
    ps = []
    while len(ps) < 20:
        p = int(gmpy2.next_prime(gmpy2.mpz(rnd(330))))
        for k in range(2, 400, 2):
            q = k * (p - 1) + 1
            n = p * q
            if q > 2 and gmpy2.is_prime(q) and pow(2, n - 1, n) == 1 and n.bit_length() <= 664:
                ps.append(n)
                break
    check("pseudoprimes (p, k(p-1)+1)", ps)
    check("special: 2^k +- small, near R", [(1 << 661) - 1, (1 << 661) + 1, (1 << 660) + 7, (1 << 664) - 1, (1 << 663) + 3, (1 << 655) | 1, (1 << 656) - 1])
    ok &= members_test(rng)
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


def members_test(rng):
    """fm13_members (member-level scheduling, first pass per member) against a plain Python loop."""
    sys.path.insert(0, HERE)
    import fm13
    import json
    camp = json.load(open(os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json")))
    N0, M = int(camp["N0"]), int(camp["M"])
    U = camp["residual"]
    fm = fm13.Members(N0, M, U)
    ok = True
    for trial, (nm, maxrows) in enumerate(((1, 5), (7, 3), (50, 40), (300, 60), (40, 2000), (9, 1))):
        kv = [rng.getrandbits(rng.choice([8, 20, 31, 33])) for _ in range(nm)]
        rows, offs = [], [0]
        for _ in range(nm):
            r = sorted(rng.sample(range(len(U)), min(len(U), rng.randint(0, maxrows)))) if maxrows > 1 else [rng.randrange(len(U))]
            rows += r
            offs.append(len(rows))
        got = fm.first_pass(kv, np.array(rows, dtype=np.uint16), np.array(offs, dtype=np.int64))
        bad = 0
        for i, k in enumerate(kv):
            exp = -1
            for pos, r in enumerate(rows[offs[i]:offs[i + 1]]):
                n = N0 + k * M - U[r]
                if pow(2, n - 1, n) == 1:
                    exp = pos
                    break
            bad += exp != got[i]
        print(f"  members trial {trial}: {nm} members, up to {maxrows} rows, {int((got >= 0).sum())} with a pass, wrong {bad}")
        ok &= bad == 0
    return ok


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tests of sieve200: the alive matrix and the counts of a block against

  (1) the definition (brute force with Python integers) on small synthetic specs,
  (2) search.py's numpy sieve (the first half of search.run_block, copied below as numpy_alive) on the campaign3 spec,
      a subset of its rows by default, all 867 rows with --full.

    python3 test_sieve200.py [--full] [--march haswell|generic|native]
"""
import argparse
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from sieve200 import Sieve200  # noqa: E402


def primes_below(n):
    s = bytearray([1]) * n
    s[:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytes(len(s[i * i::i]))
    return [i for i in range(n) if s[i]]


def brute_alive(N0, M, U, B, k0, K, exclude=()):
    """alive[r][j] unless some prime 3 <= s < B (s not dividing M, not excluded) divides N0 + (k0+j) M - U[r]."""
    S = [s for s in primes_below(B) if s >= 3 and M % s and s not in set(exclude)]
    out = np.ones((len(U), K), dtype=bool)
    for r, q in enumerate(U):
        base = N0 - q
        for j in range(K):
            n = base + (k0 + j) * M
            for s in S:
                if n % s == 0:
                    out[r, j] = False
                    break
    return out


def numpy_alive(search, k0):
    """The sieve of search.run_block, verbatim (after init_spec)."""
    G = search.G
    U, L = G["U"], G["block"]
    Ss_list = G["S_small_list"]
    S, n0m, inv, small = G["S"], G["n0m"], G["inv"], G["small"]
    alive = np.ones((len(U), L), dtype=bool)
    for i, q in enumerate(U):
        row = alive[i]
        kres = ((q - n0m) * inv - k0) % S
        js = kres[small].tolist()
        for j, s in zip(js, Ss_list):
            row[j::s] = False
        jl = kres[~small]
        hit = jl < L
        row[jl[hit]] = False
    return alive


def check(name, sv, alive_ref, k0):
    cnt, bits = sv.block(k0)
    alive = sv.alive(bits)
    ok = alive.shape == alive_ref.shape and np.array_equal(alive, alive_ref)
    okc = np.array_equal(cnt.astype(np.int64), alive_ref.sum(axis=0))
    print(f"  {name:<44s} k0={k0:<12d} alive {'ok' if ok else 'MISMATCH'}  counts {'ok' if okc else 'MISMATCH'}"
          f"  alive/k={alive_ref.sum() / alive_ref.shape[1]:.2f}", flush=True)
    if not (ok and okc):
        bad = np.argwhere(alive != alive_ref)
        print("   first differences (row, j):", bad[:5].tolist())
    return ok and okc


def synthetic(march, rng):
    ok = True
    print("synthetic specs against the definition")
    plist = primes_below(300)
    for trial in range(6):
        cover = rng.sample(plist[:30], rng.randint(5, 12))
        M = 1
        for c in cover:
            M *= c
        N0 = rng.getrandbits(rng.choice([80, 200, 330])) | 1
        qs = sorted(rng.sample([p for p in primes_below(30000) if p > 100], rng.randint(3, 40)))
        B = rng.choice([40, 330, 1000, 1700, 4000])
        logK = rng.choice([9, 10, 12])
        ex = rng.sample(plist[:25], 2) if trial % 2 else ()
        sv = Sieve200(N0, M, qs, B, logK=logK, exclude=ex, march=march)
        for k0 in (0, rng.getrandbits(20), rng.getrandbits(33), (1 << 36) + rng.getrandbits(12)):
            K = 1 << logK
            ref = brute_alive(N0, M, qs, B, k0, K, ex)
            ok &= check(f"trial {trial} B={B} K={K} rows={len(qs)} excl={len(ex)}", sv, ref, k0)
    return ok


def campaign(march, full, rng):
    import search
    ok = True
    spec = json.load(open(os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json")))
    if not full:
        spec["residual"] = spec["residual"][::6]                  # 145 rows
    cover = [r for r, _ in spec["cover"]]
    print(f"campaign3 spec, {len(spec['residual'])} rows, against search.py's numpy sieve")
    for sieve_b in ((3000, 100003) if not full else (3000, 100003, 1000003)):
        search.G.clear()
        search._SIEVE_CACHE.clear()
        search.init_spec(spec, sieve_b, 32768)
        sv = Sieve200(int(spec["N0"]), int(spec["M"]), spec["residual"], sieve_b, logK=15, exclude=cover, march=march)
        assert sv.nS == len(search.G["S"]), (sv.nS, len(search.G["S"]))
        assert np.array_equal(sv.primes(), search.G["S"]), "different sieve primes"
        for k0 in (0, 32768 * 3, 32768 * 40001 + 5):
            t = time.time()
            ref = numpy_alive(search, k0)
            tref = time.time() - t
            t = time.time()
            ok &= check(f"B={sieve_b} ({sv.nS} primes) numpy {tref:.1f}s", sv, ref, k0)
    # a K larger than the block: the rows of its first L members are search's, the others are the next blocks'
    search.G.clear()
    search._SIEVE_CACHE.clear()
    sb = 100003
    search.init_spec(spec, sb, 32768)
    sv = Sieve200(int(spec["N0"]), int(spec["M"]), spec["residual"], sb, logK=17, exclude=cover, march=march)
    k0 = 32768 * 777
    cnt, bits = sv.block(k0)
    alive = sv.alive(bits)
    for b in range(4):
        ref = numpy_alive(search, k0 + 32768 * b)
        same = np.array_equal(alive[:, 32768 * b:32768 * (b + 1)], ref)
        print(f"  K=2^17, sub-block {b}: {'ok' if same else 'MISMATCH'}")
        ok &= same
    # a window of 2^20 members (eight tiles of 2^17 bits for the small primes): sub-blocks 0, 7 and 31 against numpy
    sb = 200003
    search.G.clear()
    search._SIEVE_CACHE.clear()
    search.init_spec(spec, sb, 32768)
    sv = Sieve200(int(spec["N0"]), int(spec["M"]), spec["residual"], sb, logK=20, exclude=cover, march=march)
    k0 = 32768 * 1234
    cnt, bits = sv.block(k0)
    alive = sv.alive(bits)
    for b in (0, 7, 31):
        ref = numpy_alive(search, k0 + 32768 * b)
        same = np.array_equal(alive[:, 32768 * b:32768 * (b + 1)], ref)
        print(f"  K=2^20, sub-block {b}: {'ok' if same else 'MISMATCH'}")
        ok &= same
    ok &= np.array_equal(cnt.astype(np.int64), alive.sum(axis=0))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--march", default=None)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ok = synthetic(a.march, rng)
    ok &= campaign(a.march, a.full, rng)
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

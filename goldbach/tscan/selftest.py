#!/usr/bin/env python3
"""Self-test for tscan.c.  Needs gcc and gmpy2; takes about a minute.

1. The base-2 Fermat test (2, 3 and 4 limbs) against gmpy2.powmod on about
   80,000 odd numbers per size: random, primes and their neighbours,
   base-2 pseudoprimes, products p*(2p - 1).
2. A full scan of a small progression (Q = 3001, 54 residual primes,
   k < 65536) against a brute-force reference that calls gmpy2.is_prime on
   every N - q: the reported k must be exactly the same set.
3. Block size, sieve bound and thread count must not change the result, and
   a selection threshold T must report exactly the successes with at most T
   survivors (checked through the histogram, which must not depend on T).
"""
import json
import os
import random
import subprocess
import sys

import gmpy2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scan  # noqa: E402


def run(exe, args, threads=2, stdin=None):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads))
    return subprocess.run([exe] + [str(a) for a in args], input=stdin, capture_output=True, text=True,
                          check=True, env=env).stdout


def test_fermat():
    random.seed(20261122)
    for nl in (2, 3, 4):
        exe, W = scan.build(nl), 64 * nl
        nums = [341, 561, 645, 1105, 1387, 1729, 2047, 3277, 4033, 4369, 4371, 8321, 65537, 3215031751,
                2**61 - 1, 2**89 - 1, (2**31 - 1) * (2**61 - 1), 2**(W - 1) - 1, 2**(W - 2) + 1]
        for _ in range(60000):
            b = random.randint(10, W - 1)
            nums.append(random.getrandbits(b) | (1 << (b - 1)) | 1)
        for _ in range(6000):
            b = random.randint(10, W - 1)
            p = int(gmpy2.next_prime(random.getrandbits(b) | (1 << (b - 1))))
            nums += [p, p + 2, p - 2]
        for _ in range(300):
            b = random.randint(8, (W - 2) // 2)
            p = int(gmpy2.next_prime(random.getrandbits(b) | (1 << (b - 1))))
            if gmpy2.is_prime(2 * p - 1):
                nums.append(p * (2 * p - 1))
        nums = [n for n in nums if n % 2 and 10 <= n.bit_length() <= W - 1]
        out = run(exe, ["--fermat"], stdin="\n".join(f"{n:x}" for n in nums) + "\n").split()
        assert len(out) == len(nums)
        bad = [n for n, o in zip(nums, out) if o != str(int(gmpy2.powmod(2, n - 1, n) == 1))]
        assert not bad, bad[:3]
        print(f"fermat, {nl} limbs: {len(nums)} numbers agree with gmpy2 ({out.count('1')} pass base 2)")


def test_scan():
    spec = json.load(open(os.path.join(HERE, "selftest_q3001.json")))
    job = os.path.join(HERE, "selftest_q3001.job")
    scan.write_job(spec, job)
    N0, M, U, kmax = int(spec["N0"]), int(spec["M"]), spec["residual"], 65536
    ref = [k for k in range(kmax) if not any(gmpy2.is_prime(N0 + k * M - q) for q in U)]
    assert len(ref) >= 3, ref

    def reported(nl, B, logK, T, threads):
        out = run(scan.build(nl), [job, 0, kmax, B, logK, T], threads).splitlines()
        st = [l for l in out if l.startswith("STATS")][0]
        return sorted(int(l.split()[1]) for l in out if l.startswith("S ")), st.split("hist=")[1]

    base, hist = reported(2, 131072, 14, 255, 2)
    assert base == ref, (base, ref)
    print(f"scan: {len(ref)} successes for k < {kmax}, identical to the brute-force reference: {ref}")
    for nl, B, logK, threads in ((2, 3000, 12, 1), (2, 1000000, 16, 4), (3, 131072, 17, 2), (4, 40000, 10, 3)):
        got, h = reported(nl, B, logK, 255, threads)
        assert got == ref, (nl, B, logK, threads, got)
        if B == 131072:
            assert h == hist
    print("scan: same successes for other limb counts, sieve bounds, block sizes and thread counts")
    T = 14
    got, h = reported(2, 131072, 14, T, 2)
    assert h == hist and set(got) <= set(ref)
    # a success has all its survivors composite; count them independently to predict which pass the threshold
    small = [s for s in range(3, 131073, 2) if gmpy2.is_prime(s) and M % s]
    want = [k for k in ref
            if sum(all((N0 + k * M - q) % s for s in small) for q in U) <= T]
    assert got == want, (got, want)
    print(f"scan: with T = {T} exactly the {len(want)} successes with at most {T} survivors are reported")
    os.remove(job)


if __name__ == "__main__":
    test_fermat()
    test_scan()
    print("ALL TESTS PASSED")

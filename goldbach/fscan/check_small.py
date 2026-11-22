#!/usr/bin/env python3
"""End-to-end check of fscan on a small threshold, where successes are frequent.

    python3 check_small.py [Q [Rmax [Xmax [nvec [theta [Ta]]]]]]      default 3001 51 1e20 150 24 30
    FSCAN=./other_build python3 check_small.py ...

1. Brute force (gmpy2.is_prime on every row of every member) on nvec vectors gives the true successes.
2. fscan with the thresholds off (theta 0, Ta 255) must report exactly those members on those vectors.
3. fscan with selective thresholds must report a subset of the truth, and over ALL vectors its
   "expected" figure must agree with the number it found.
"""
import os
import random
import subprocess
import sys

import gmpy2

A = sys.argv[1:]
Q = int(A[0]) if len(A) > 0 else 3001
RMAX = int(A[1]) if len(A) > 1 else 51
XMAX = int(float(A[2])) if len(A) > 2 else 10**20
NVEC = int(A[3]) if len(A) > 3 else 150
THETA = int(A[4]) if len(A) > 4 else 24
TA = int(A[5]) if len(A) > 5 else 30
XMIN = 4 * 10**18
L = 383
EXE = os.environ.get("FSCAN", "./fscan")
COVER = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
M = 2
for r in COVER:
    M *= r
rows_all = [q for q in range(3, Q, 2) if gmpy2.is_prime(q)]


def run(*args):
    out = subprocess.run([EXE, str(Q), str(L)] + [str(a) for a in args], capture_output=True, text=True, check=True).stdout
    lines = out.splitlines()
    succ = {}
    for l in lines:
        if l.startswith("S "):
            f = l.split()
            succ.setdefault(int(f[3]), set()).add(int(f[1]))
    st = [l for l in lines if l.startswith("STATS")]
    stats = dict(kv.split("=") for kv in st[0].split(" | ")[1].split()) if st else {}
    return lines, succ, stats


vecs = {}
for line in run(0, RMAX, 0, 0, 0, 0, "dump=1")[0]:
    if line.startswith("V "):
        f = line.split()
        vecs[int(f[1])] = list(map(int, f[3:]))
print(f"{EXE}, Q={Q}: {len(vecs)} vectors with at most {RMAX} residual primes; M={M}")
random.seed(7)
pick = sorted(vecs, key=lambda n0: (len(vecs[n0]), n0))[:20] + random.sample(sorted(vecs), min(NVEC, len(vecs)))
pick = sorted(set(pick))
truth, bad_cover = {}, 0
for n0 in pick:
    res = vecs[n0]
    for q in rows_all:                   # every non-residual row must be killed by a cover prime
        if q not in set(res) and not any((n0 - q) % r == 0 for r in COVER):
            bad_cover += 1
    k0 = (XMIN - n0) // M + 1
    k1 = (XMAX - n0) // M
    t = set()
    for k in range(k0, k1 + 1):
        N = n0 + k * M
        if not any(gmpy2.is_prime(N - q) for q in res):
            assert not any(gmpy2.is_prime(N - q) for q in rows_all), N
            t.add(N)
    truth[n0] = t
ntrue = sum(len(t) for t in truth.values())
members = sum((XMAX - n0) // M - (XMIN - n0) // M for n0 in pick)
print(f"brute force on {len(pick)} vectors, {members} members: {ntrue} successes; rows not covered and not residual: {bad_cover}")
ok = bad_cover == 0

# thresholds off, all vectors in one run; theta is relative to the residual size, so rref = RMAX and theta = -RMAX gives 0
_, succ, st = run(0, RMAX, XMIN, XMAX, -RMAX, 255, f"rref={RMAX}")
same = all(succ.get(n0, set()) == truth[n0] for n0 in pick)
ok &= same
for n0 in pick:
    if succ.get(n0, set()) != truth[n0]:
        print(f"  MISMATCH n0={n0}: fscan {len(succ.get(n0, set()))}, truth {len(truth[n0])}")
print(f"thresholds off: {st['found']} reported on all vectors ({st['members']} members, expected {float(st['expected']):.1f}); "
      f"identical to brute force on each of the {len(pick)} checked vectors: {same}")

# selective thresholds, all vectors
_, succ, st = run(0, RMAX, XMIN, XMAX, THETA, TA, f"rref={RMAX}")
sub = all(succ.get(n0, set()) <= truth[n0] for n0 in pick)
ok &= sub
found, exp = int(st["found"]), float(st["expected"])
agree = abs(found - exp) < 4 * exp ** 0.5 + 0.1 * exp
ok &= agree
print(f"theta={THETA} (at {RMAX} residual primes) Ta={TA}: tested {st['kept']} of {st['members']} members "
      f"({100 * int(st['kept']) / int(st['members']):.2f}%), found {found}, expected {exp:.1f} (raw {float(st['expected_raw']):.1f}); "
      f"subset of the truth on the checked vectors: {sub}")
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)

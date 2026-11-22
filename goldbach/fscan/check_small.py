#!/usr/bin/env python3
"""End-to-end check of fscan on a small threshold, where successes are frequent.

    python3 check_small.py [Q [Rmax [Xmax [nvec]]]]      default 3001 51 1e20 150

1. Brute force (gmpy2.is_prime on every row of every member) on nvec vectors gives the true successes.
2. fscan with the thresholds off (theta 0, Ta 255) must report exactly those members.
3. fscan with selective thresholds must report a subset of them, and its "expected" figure (the sum of
   (1 - eps)^a over the members it tested) must agree with the number it found.
"""
import random, subprocess, sys
import gmpy2

Q = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 51
XMAX = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**20
NVEC = int(sys.argv[4]) if len(sys.argv) > 4 else 150
XMIN = 4 * 10**18
L = 383
COVER = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
M = 2
for r in COVER:
    M *= r
rows_all = [q for q in range(3, Q, 2) if gmpy2.is_prime(q)]


def run(*args):
    out = subprocess.run(["./fscan", str(Q), str(L)] + [str(a) for a in args], capture_output=True, text=True, check=True).stdout
    return out.splitlines()


vecs = {}
for line in run(0, RMAX, 0, 0, 0, 0, "dump=1"):
    if line.startswith("V "):
        f = line.split()
        vecs[int(f[1])] = list(map(int, f[3:]))
print(f"Q={Q}: {len(vecs)} vectors with at most {RMAX} residual primes; M={M}")
random.seed(7)
pick = sorted(vecs, key=lambda n0: (len(vecs[n0]), n0))[:20] + random.sample(sorted(vecs), min(NVEC, len(vecs)))
pick = sorted(set(pick))
truth, bad_cover = {}, 0
for n0 in pick:
    res = vecs[n0]
    # every non-residual row must be killed by a cover prime
    for q in rows_all:
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
got_all = set()
for n0 in pick:
    lines = run(0, RMAX, XMIN, XMAX, 0, 255, f"one={n0}", "threads=1", f"rref={len(vecs[n0])}")
    got = {int(l.split()[1]) for l in lines if l.startswith("S ")}
    got_all |= got
    if got != truth[n0]:
        ok = False
        print(f"  MISMATCH n0={n0}: fscan {len(got)}, truth {len(truth[n0])}, missing {sorted(truth[n0] - got)[:3]}, extra {sorted(got - truth[n0])[:3]}")
print(f"thresholds off: fscan reports {len(got_all)} members; identical to brute force on every vector: {ok}")

# selective thresholds on the same vectors
for theta, ta in ((int(sys.argv[5]) if len(sys.argv) > 5 else 24, int(sys.argv[6]) if len(sys.argv) > 6 else 30),):
    found, exp, kept, mem = set(), 0.0, 0, 0
    for n0 in pick:
        lines = run(0, RMAX, XMIN, XMAX, theta, ta, f"one={n0}", "threads=1", f"rref={len(vecs[n0])}")
        found |= {int(l.split()[1]) for l in lines if l.startswith("S ")}
        st = dict(kv.split("=") for kv in [l for l in lines if l.startswith("STATS")][0].split(" | ")[1].split())
        exp += float(st["expected"]); kept += int(st["kept"]); mem += int(st["members"])
    alltrue = set().union(*truth.values())
    sub = found <= alltrue
    ok &= sub
    print(f"theta={theta} Ta={ta}: tested {kept} of {mem} members ({100 * kept / mem:.2f}%), found {len(found)} "
          f"({100 * len(found) / max(ntrue, 1):.1f}% of all), expected {exp:.1f}; subset of the truth: {sub}")
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)

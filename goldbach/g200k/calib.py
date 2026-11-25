#!/usr/bin/env python3
"""Hit-rate calibration: is (1 - p)^a, a = a member's survivors after the sieve, the chance that all its rows are composite?

    python3 calib.py cover.txt Q kstart nmembers skip B out.json [--procs P] [--logK 20]

The scan of search_c.py (sieve200 to B, the emptiest 1 - skip of each 32,768-block, fm13 / fmw Fermat until the first
probable prime), on rows = the odd primes below Q in no class of the cover, members k in [kstart, kstart + nmembers).
Recorded: the histogram of the tested members' survivor counts, tests and probable primes (p^ = prp / tests, the per-survivor
chance), every member whose survivors are all composite (verified: N - q composite for every prime q < Q, gmpy2 BPSW).
Expected hits = sum over the histogram of n(a) (1 - p^)^a, exactly the model's prediction for the members tested.
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sieve200")); sys.path.insert(0, os.path.join(HERE, "..", "fermat661")); sys.path.insert(0, os.path.join(HERE, "..", "fermatw"))
import gmpy2
from sieve200 import Sieve200
from sympy import primerange

args = sys.argv[1:]
procs = 1; logK = 20
if "--procs" in args:
    i = args.index("--procs"); procs = int(args[i + 1]); del args[i:i + 2]
if "--logK" in args:
    i = args.index("--logK"); logK = int(args[i + 1]); del args[i:i + 2]
cover_path, Q, kstart, nmem, skip, B, out = args[0], int(args[1]), int(args[2]), int(args[3]), float(args[4]), int(args[5]), args[6]
line = next(l for l in open(cover_path) if l.startswith("BEST") or l.startswith("COVER")).split()
cov = [tuple(map(int, t.split(":"))) for t in (line[1:] if line[0] == "BEST" else line[2:])]
M, N0 = 2, 0
for r, a in cov:
    t = ((a - N0) * pow(M, -1, r)) % r
    N0 += M * t; M *= r
U = [q for q in primerange(3, Q) if all(q % r != a for r, a in cov)]
BL = 32768
G = {}


def init():
    sv = Sieve200(N0, M, U, B, logK=logK, exclude=[r for r, _ in cov])
    bits = (N0 + (kstart + nmem) * M).bit_length()
    if bits <= 672:
        import fm13
        fm13.load(); fm = fm13.Members(N0, M, U)
    else:
        import fmw
        fm = fmw.Members(N0, M, U, kstart + nmem)
    G.update(sv=sv, fm=fm)


def window(k0):
    sv, fm = G["sv"], G["fm"]
    cnt, bits = sv.block(k0)
    hist = np.zeros(len(U) + 1, dtype=np.int64)
    tests = prps = 0
    cands = []
    for b in range(0, sv.K, BL):
        c = cnt[b:b + BL].astype(np.int64)
        keep = int(math.ceil(BL * (1 - skip)))
        order = np.argsort(c, kind="stable")[:keep]
        np.add.at(hist, c[order], 1)
        js = np.ascontiguousarray(order + b, dtype=np.uint32)
        rows, offs = sv.survivors(bits, js)
        fp = fm.first_pass(js.astype(np.uint64) + k0, rows, offs)
        ln = np.diff(offs)
        tests += int(np.where(fp >= 0, fp + 1, ln).sum())
        prps += int((fp >= 0).sum())
        for t in np.nonzero(fp < 0)[0]:
            cands.append(int(js[t]) + k0)
    return hist, tests, prps, cands


def verify(k):
    N = N0 + k * M
    for q in primerange(2, Q):
        if gmpy2.is_prime(N - q):
            return None
    g = int(gmpy2.next_prime(Q - 1))
    while not gmpy2.is_prime(N - g):
        g = int(gmpy2.next_prime(g))
    return {"k": k, "digits": len(str(N)), "g": g}


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    init()
    K = G["sv"].K
    starts = list(range(kstart, kstart + nmem, K))
    hist = np.zeros(len(U) + 1, dtype=np.int64); tests = prps = 0; cands = []
    with mp.Pool(procs, initializer=init) as pool:
        for h, t, p, c in pool.imap_unordered(window, starts):
            hist += h; tests += t; prps += p; cands += c
    hits = [r for r in (verify(k) for k in sorted(cands)) if r]
    p = prps / tests
    se = math.sqrt(p * (1 - p) / tests) / math.sqrt(max(1e-12, 1 - p))         # geometric MLE, approximate standard error
    a = np.arange(len(hist))
    expd = lambda pp: float((hist * (1 - pp) ** a).sum())
    members = len(starts) * K
    res = {"cover": os.path.basename(cover_path), "Q": Q, "rows": len(U), "kstart": kstart, "members": members, "skip": skip, "B": B,
           "tested": int(hist.sum()), "tests": tests, "prp": prps, "p_hat": p, "p_se": se,
           "expected": expd(p), "expected_lo": expd(p + se), "expected_hi": expd(p - se),
           "mean_tested_count": float((hist * a).sum() / hist.sum()), "found": len(hits), "candidates": len(cands), "hits": hits,
           "digits_max": len(str(N0 + (kstart + members - 1) * M)), "cpu_seconds": (time.time() - t0) * procs,
           "hist": {int(i): int(v) for i, v in enumerate(hist) if v}}
    json.dump(res, open(out, "w"))
    print(f"{os.path.basename(cover_path)} Q={Q} rows={len(U)}: {members} members (k from {kstart}), {res['tested']} tested, {tests} tests, "
          f"p^={p:.5f}+-{se:.5f}; expected {res['expected']:.2f} ({res['expected_lo']:.2f}..{res['expected_hi']:.2f}), found {len(hits)} "
          f"(candidates {len(cands)}); E_tested={res['mean_tested_count'] * -math.log(1 - p):.2f}; {res['cpu_seconds'] / 3600:.2f} CPU-h; "
          f"digits <= {res['digits_max']}", flush=True)

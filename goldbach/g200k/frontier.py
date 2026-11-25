#!/usr/bin/env python3
"""Closeness frontier rungs (doubling as hit-rate calibration): every N with d digits and N <= c 10^(d-1) whose N - q are all
composite for the primes q < Q = ceil(0.10 * closeness.ceiling(ln(c 10^(d-1)))) has closeness >= 10% at d digits.

    python3 frontier.py covers.txt d c_num c_den ncovers skip B out.json [--procs P] [--frac F] [--logK 22]

covers.txt: COVER / BEST lines for one set of moduli (ptcover's PT_DUMP); the first ncovers distinct ones, fewest rows first.
c = c_num / c_den (e.g. 11 10 for 1.1).  Each cover's progression N0 + k M is scanned over its k window (10^(d-1), c 10^(d-1)]
(the first fraction F of it with --frac) by calib.py's scan: sieve200 to B, the emptiest 1 - skip of each 32,768-block of
in-window members, fm13 / fmw until the first probable prime.  Recorded per rung: the histogram of tested survivor counts,
tests and PRPs (p^), the hits (verified: N - q composite for every prime q < Q; then g and closeness from N alone), and the
expected hits sum n(a) (1 - p^)^a."""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
GB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(GB, "sieve200")); sys.path.insert(0, os.path.join(GB, "fermat661")); sys.path.insert(0, os.path.join(GB, "fermatw")); sys.path.insert(0, GB)
import gmpy2
from sieve200 import Sieve200
from sympy import primerange
import closeness

args = sys.argv[1:]
procs, frac, logK = 1, 1.0, 22
for flag in ("--procs", "--frac", "--logK"):
    if flag in args:
        i = args.index(flag); v = args[i + 1]; del args[i:i + 2]
        if flag == "--procs": procs = int(v)
        elif flag == "--frac": frac = float(v)
        else: logK = int(v)
src, d, cn, cd, ncov, skip, B, out = args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4]), float(args[5]), int(args[6]), args[7]
LO = 10 ** (d - 1)
HI = cn * 10 ** (d - 1) // cd                                        # N <= HI
Q = math.ceil(0.10 * closeness.ceiling(math.log(cn / cd) + (d - 1) * math.log(10)))
BL = 32768

covers, seen = [], set()
for l in open(src):
    t = l.split()
    if not t or t[0] not in ("COVER", "BEST"):
        continue
    cov = tuple(tuple(map(int, p.split(":"))) for p in (t[2:] if t[0] == "COVER" else t[1:]))
    if cov in seen:
        continue
    seen.add(cov); covers.append((int(t[1]) if t[0] == "COVER" else 10 ** 9, cov))
covers.sort(key=lambda x: x[0])
covers = covers[:ncov]                                               # the dump's k is the cover's row count at its own Q
primes = list(primerange(3, Q))
specs = []
for _, cov in covers:
    rows = [q for q in primes if all(q % r != a for r, a in cov)]
    M, N0 = 2, 0
    for r, a in cov:
        tt = ((a - N0) * pow(M, -1, r)) % r
        N0 += M * tt; M *= r
    klo = max(0, -(-(LO + 1 - N0) // M))                             # N0 + k M > 10^(d-1)
    khi = (HI - N0) // M                                             # N0 + k M <= c 10^(d-1)
    khi = klo + int((khi - klo + 1) * frac) - 1
    if khi >= klo:
        specs.append(dict(N0=N0, M=M, U=rows, cover=cov, klo=klo, khi=khi))
specs.sort(key=lambda s: len(s["U"]))
specs = specs[:ncov]
G = {}


def task_list():
    tasks = []
    for ci, s in enumerate(specs):
        K = 1 << logK
        for k0 in range(s["klo"] - s["klo"] % BL, s["khi"] + 1, K):   # from the 32,768-block of klo: the blocks stay at multiples of BL
            tasks.append((ci, k0))
    return tasks


def window(task):
    ci, k0 = task
    s = specs[ci]
    if G.get("ci") != ci:
        G["sv"] = Sieve200(s["N0"], s["M"], s["U"], B, logK=logK, exclude=[r for r, _ in s["cover"]])
        bits = (s["N0"] + (s["khi"] + 1) * s["M"]).bit_length()
        import fmw
        if fmw.limbs_for(bits) >= 13 and bits <= 672:                # fm13 only where fmw would need 13 limbs as well: at 101
            import fm13; fm13.load(); G["fm"] = fm13.Members(s["N0"], s["M"], s["U"])   # digits fmw's 7 limbs are 3.0x faster
        else:
            G["fm"] = fmw.Members(s["N0"], s["M"], s["U"], s["khi"] + 1)
        G["ci"] = ci
    sv, fm = G["sv"], G["fm"]
    cnt, bits = sv.block(k0)
    hist = np.zeros(len(s["U"]) + 1, dtype=np.int64)
    tests = prps = members = 0
    cands = []
    kk = k0 + np.arange(sv.K)
    valid = (kk >= s["klo"]) & (kk <= s["khi"])
    for b in range(0, sv.K, BL):
        v = np.nonzero(valid[b:b + BL])[0]
        if not len(v):
            continue
        members += len(v)
        c = cnt[b:b + BL].astype(np.int64)[v]
        keep = int(math.ceil(len(v) * (1 - skip)))
        order = v[np.argsort(c, kind="stable")[:keep]]
        np.add.at(hist, cnt[b:b + BL].astype(np.int64)[order], 1)
        js = np.ascontiguousarray(order + b, dtype=np.uint32)
        rows, offs = sv.survivors(bits, js)
        fp = fm.first_pass(js.astype(np.uint64) + k0, rows, offs)
        tests += int(np.where(fp >= 0, fp + 1, np.diff(offs)).sum())
        prps += int((fp >= 0).sum())
        cands += [int(js[t]) + k0 for t in np.nonzero(fp < 0)[0]]
    return ci, hist, tests, prps, members, cands


def verify(ci, k):
    s = specs[ci]
    N = s["N0"] + k * s["M"]
    for q in primerange(2, Q):
        if gmpy2.is_prime(N - q):
            return None
    g = int(gmpy2.next_prime(Q - 1))
    while not gmpy2.is_prime(N - g):
        g = int(gmpy2.next_prime(g))
    return {"cover": ci, "k": k, "N": str(N), "digits": len(str(N)), "g": g,
            "closeness": g / closeness.ceiling(closeness.ln_int(N))}


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    tasks = task_list()
    H = {}; tests = prps = members = 0; cands = []
    with mp.Pool(procs) as pool:
        for ci, h, t, p, m, c in pool.imap_unordered(window, tasks):
            H[ci] = H.get(ci, 0) + h; tests += t; prps += p; members += m; cands += [(ci, k) for k in c]
    hits = [r for r in (verify(ci, k) for ci, k in sorted(cands)) if r]
    p = prps / tests
    se = math.sqrt(p * (1 - p) / tests) / math.sqrt(max(1e-12, 1 - p))
    expd = lambda pp: float(sum((h * (1 - pp) ** np.arange(len(h))).sum() for h in H.values()))
    hist_all = {}
    for h in H.values():
        for a, n in enumerate(h):
            if n: hist_all[a] = hist_all.get(a, 0) + int(n)
    tested = sum(hist_all.values())
    mean_a = sum(a * n for a, n in hist_all.items()) / tested
    rows = [len(s["U"]) for s in specs]
    res = {"digits": d, "c": [cn, cd], "Q": Q, "moduli": len(specs[0]["cover"]), "covers": len(specs), "rows_min": min(rows), "rows_max": max(rows),
           "members": members, "tested": tested, "tests": tests, "prp": prps, "p_hat": p, "p_se": se, "expected": expd(p),
           "expected_lo": expd(p + se), "expected_hi": expd(p - se), "E_tested": mean_a * -math.log(1 - p), "found": len(hits),
           "candidates": len(cands), "hits": hits, "cpu_seconds": (time.time() - t0) * procs, "hist": hist_all,
           "covers_used": [" ".join(f"{r}:{a}" for r, a in s["cover"]) for s in specs]}
    json.dump(res, open(out, "w"))
    print(f"d={d} c={cn}/{cd} Q={Q}: {len(specs)} covers ({len(specs[0]['cover'])} moduli, rows {min(rows)}..{max(rows)}), {members} members, "
          f"{tested} tested, p^={p:.5f}; expected {res['expected']:.2f} ({res['expected_lo']:.2f}..{res['expected_hi']:.2f}), found {len(hits)} "
          f"(candidates {len(cands)}); E_tested={res['E_tested']:.2f}; {res['cpu_seconds'] / 3600:.2f} CPU-h; best closeness "
          f"{max([h['closeness'] for h in hits], default=0):.4f}", flush=True)

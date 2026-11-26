#!/usr/bin/env python3
"""Closeness frontier rungs (doubling as hit-rate calibration): every N with d digits and N <= c 10^(d-1) whose N - q are all
composite for the primes q < Q = ceil(0.10 * closeness.ceiling(ln(c 10^(d-1)))) has closeness >= 10% at d digits.

    python3 frontier.py covers.txt d c_num c_den ncovers skip B out.json [--procs P] [--frac F] [--logK 22] [--cover-offset X]

covers.txt: COVER / BEST lines for one set of moduli (ptcover's PT_DUMP).  Ranking: the first 4,000 distinct ones by the
dump's k, sorted by their rows at this Q (ties: dump order); a run takes ncovers of them from --cover-offset on (default 0),
so runs with different offsets scan disjoint covers.  (The 101-, 105- and 110-digit rungs ranked only the first ncovers by
the dump's k; covers_used in each output lists the covers exactly.)
c = c_num / c_den (e.g. 11 10 for 1.1).  Each cover's progression N0 + k M is scanned over its k window (10^(d-1), c 10^(d-1)]
(the first fraction F of it with --frac) by calib.py's scan: sieve200 to B, the emptiest 1 - skip of each 32,768-block of
in-window members, fm13 / fmw until the first probable prime.  Recorded per rung: the histogram of tested survivor counts,
tests and PRPs (p^), the hits (verified: N - q composite for every prime q < Q; then g and closeness from N alone), and the
expected hits sum n(a) (1 - p^)^a."""
import ctypes, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
GB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(GB, "sieve200")); sys.path.insert(0, os.path.join(GB, "fermat661")); sys.path.insert(0, os.path.join(GB, "fermatw")); sys.path.insert(0, GB)
import gmpy2
from sieve200 import Sieve200
from sympy import primerange
import closeness

args = sys.argv[1:]
procs, frac, logK, cov_off = 1, 1.0, 22, 0
for flag in ("--procs", "--frac", "--logK", "--cover-offset"):
    if flag in args:
        i = args.index(flag); v = args[i + 1]; del args[i:i + 2]
        if flag == "--procs": procs = int(v)
        elif flag == "--frac": frac = float(v)
        elif flag == "--logK": logK = int(v)
        else: cov_off = int(v)                                       # skip the first cov_off covers (a rung split over runs)
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
covers.sort(key=lambda x: x[0])                                      # stable: ties keep the file's order
POOL = 4000                                                          # the covers ranked by their rows at this Q: the first POOL by
covers = covers[:max(POOL, cov_off + ncov)]                          # the dump's k (rows at the dump's own Q), so that runs with
primes = list(primerange(3, Q))                                      # different offsets split one ranking
P = np.array(primes, dtype=np.int64)
specs = []
for idx, (_, cov) in enumerate(covers):
    alive = np.ones(len(P), dtype=bool)
    for r, a in cov:
        alive &= (P % r) != a
    rows = P[alive].tolist()
    M, N0 = 2, 0
    for r, a in cov:
        tt = ((a - N0) * pow(M, -1, r)) % r
        N0 += M * tt; M *= r
    klo = max(0, -(-(LO + 1 - N0) // M))                             # N0 + k M > 10^(d-1)
    khi = (HI - N0) // M                                             # N0 + k M <= c 10^(d-1)
    khi = klo + int((khi - klo + 1) * frac) - 1
    if khi >= klo:
        specs.append(dict(N0=N0, M=M, U=rows, cover=cov, klo=klo, khi=khi, idx=idx))
specs.sort(key=lambda s: (len(s["U"]), s["idx"]))                    # fewest rows first, then the dump's order
specs = specs[cov_off:cov_off + ncov]
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
    sv, fm, lib = G["sv"], G["fm"], G["sv"].lib
    nU = len(s["U"])
    if G.get("bits") is None or G["bits"].shape != (nU, sv.words):
        G["bits"] = np.empty((nU, sv.words), dtype=np.uint64)       # one buffer for every window: no page faults a window
    cnt, bits = sv.block(k0, bits=G["bits"])
    hist = np.zeros(nU + 1, dtype=np.int64)
    tests = prps = members = 0
    cands = []
    order, rank = np.empty(BL, dtype=np.uint32), np.empty(BL, dtype=np.uint32)
    hs, selb = np.empty(nU + 2, dtype=np.uint32), np.empty(BL // 64, dtype=np.uint64)
    ha, hk, at = ctypes.c_double(), ctypes.c_double(), ctypes.c_int64()
    for b in range(0, sv.K, BL):
        lo, hi = max(s["klo"] - (k0 + b), 0), min(s["khi"] - (k0 + b), BL - 1)   # the members of the window: offsets lo..hi
        if hi < lo:
            continue
        nv = hi - lo + 1
        members += nv
        cb = cnt[b:b + BL]
        keep = int(math.ceil(nv * (1 - skip)))
        if nv == BL:                                                 # s200_select: the order of np.argsort(cb, kind="stable")[:keep]
            n = lib.s200_select(cb.ctypes.data, BL, keep, nU, 0.1, order.ctypes.data, ctypes.byref(ha), ctypes.byref(hk),
                                ctypes.byref(at), hs.ctypes.data)
            sel = order[:n]
        else:
            sel = np.ascontiguousarray(lo + np.argsort(cb[lo:hi + 1], kind="stable")[:keep], dtype=np.uint32)
        n = len(sel)
        hist += np.bincount(cb[sel], minlength=nU + 1)
        offs, cursor = np.empty(n + 1, dtype=np.int64), np.empty(n, dtype=np.int64)
        cap = int(cb[sel].astype(np.int64).sum())
        rows = np.empty(max(cap, 1), dtype=np.uint16)
        tot = lib.s200_csr(sv.ctx, bits.ctypes.data, ctypes.c_uint64(b // 64), BL, sel.ctypes.data, n, cb.ctypes.data,
                           rank.ctypes.data, selb.ctypes.data, cursor.ctypes.data, offs.ctypes.data, rows.ctypes.data, cap)
        assert tot == cap                                            # rows by member, ascending (as s200_extract): row by row reads
        kv = sel.astype(np.uint64) + np.uint64(k0 + b)
        fp = fm.first_pass(kv, rows[:cap], offs)
        tests += int(np.where(fp >= 0, fp + 1, np.diff(offs)).sum())
        prps += int((fp >= 0).sum())
        cands += [int(kv[t]) for t in np.nonzero(fp < 0)[0]]
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
    res = {"digits": d, "c": [cn, cd], "Q": Q, "cover_offset": cov_off, "skip": skip, "B": B, "logK": logK, "moduli": len(specs[0]["cover"]), "covers": len(specs), "rows_min": min(rows), "rows_max": max(rows),
           "members": members, "tested": tested, "tests": tests, "prp": prps, "p_hat": p, "p_se": se, "expected": expd(p),
           "expected_lo": expd(p + se), "expected_hi": expd(p - se), "E_tested": mean_a * -math.log(1 - p), "found": len(hits),
           "candidates": len(cands), "hits": hits, "cpu_seconds": (time.time() - t0) * procs, "hist": hist_all,
           "covers_used": [" ".join(f"{r}:{a}" for r, a in s["cover"]) for s in specs]}
    json.dump(res, open(out, "w"))
    print(f"d={d} c={cn}/{cd} Q={Q}: {len(specs)} covers ({len(specs[0]['cover'])} moduli, rows {min(rows)}..{max(rows)}), {members} members, "
          f"{tested} tested, p^={p:.5f}; expected {res['expected']:.2f} ({res['expected_lo']:.2f}..{res['expected_hi']:.2f}), found {len(hits)} "
          f"(candidates {len(cands)}); E_tested={res['E_tested']:.2f}; {res['cpu_seconds'] / 3600:.2f} CPU-h; best closeness "
          f"{max([h['closeness'] for h in hits], default=0):.4f}", flush=True)

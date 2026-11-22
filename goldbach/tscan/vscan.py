#!/usr/bin/env python3
"""Scan many progressions with the same modulus in lockstep (smallest N first).

    python3 vscan.py variants.json state.json <seconds> [umax] [log2 chunk]

variants.json comes from variants.py: residue vectors on the same cover
primes, i.e. progressions N = N0_v + k*M with one M.  The driver always
advances the progression whose position k is lowest, by one chunk, so all
of them climb together and N grows as slowly as possible for the work done.
Only variants with at most umax residual primes are used (default: all).
Adding variants later (a larger file or umax, same state file) is fine: the
new ones start at k = 0 and catch up first.

It stops when a success is known and no progression can still produce a
smaller one (every position is past it), or when the time is up.  State:
{"pos": {name: next k}, "found": [...], "exp_hits", "seconds"}.

The selection threshold T is kept per residual size and re-derived from
each chunk's histogram, as in scan.py.  Every reported k is re-checked
with search.verify_success before it is recorded.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import scan    # noqa: E402
import search  # noqa: E402

B, LOGK = 131072, 18


def main():
    specs = json.load(open(sys.argv[1]))
    st_path, deadline = sys.argv[2], time.time() + float(sys.argv[3])
    umax = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    chunk = 1 << (int(sys.argv[5]) if len(sys.argv) > 5 else 24)
    specs = [s for s in specs if len(s["residual"]) <= umax]
    M = int(specs[0]["M"])
    assert all(int(s["M"]) == M for s in specs)
    st = {"pos": {}, "found": [], "exp_hits": 0.0, "seconds": 0.0}
    if os.path.exists(st_path):
        st.update(json.load(open(st_path)))
    pos = st["pos"]
    for s in specs:
        pos.setdefault(s["name"], 0)
    jobdir = st_path + ".jobs"
    os.makedirs(jobdir, exist_ok=True)
    exe = scan.build(((M << 44).bit_length() + 1 + 63) // 64)

    def jobfile(s):
        path = os.path.join(jobdir, s["name"] + ".job")
        if not os.path.exists(path):
            scan.write_job(s, path)
        return path

    def best_n():
        return min((int(f["N"]) for f in st["found"]), default=None)

    def save():
        json.dump(st, open(st_path + ".tmp", "w"))
        os.replace(st_path + ".tmp", st_path)

    order = sorted(specs, key=lambda s: (len(s["residual"]), s["name"]))
    k_cal = max(min(pos[s["name"]] for s in order), 1 << 26)
    t_sieve, t_test, p, hist = scan.calibrate(exe, jobfile(order[0]), k_cal, B, LOGK)
    T = {}                                            # residual size -> threshold
    T0 = scan.best_threshold(hist, p, t_sieve, t_test)[0]
    print(f"{len(order)} progressions, residual sizes {len(order[0]['residual'])}..{len(order[-1]['residual'])}, "
          f"M has {len(str(M))} digits; calibration at k={k_cal}: sieve {t_sieve * 1e9:.1f} ns/k, Fermat test "
          f"{t_test * 1e9:.0f} ns (wall clock), p={p:.3f}", flush=True)
    t_start, calls, level_seen = time.time(), 0, None
    tests = prps = 0
    while time.time() + 30 < deadline:
        s = min(order, key=lambda s: pos[s["name"]])          # lowest position; ties: smallest residual
        k0 = pos[s["name"]]
        best = best_n()
        if best is not None and int(s["N0"]) + k0 * M >= best:
            print(f"done: every progression is past the smallest success", flush=True)
            break
        if k0 != level_seen:
            level_seen = k0
            print(f"level k={k0:,} (N up to {len(str((k0 + chunk) * M))} digits): expected hits so far "
                  f"{st['exp_hits']:.3f}, {st['seconds'] + time.time() - t_start:.0f}s", flush=True)
        u = len(s["residual"])
        stats, hist, ks = scan.scan(exe, jobfile(s), max(k0, scan.first_k(s)), k0 + chunk, B, LOGK,
                                    T.get(u, T0 + u - len(order[0]["residual"])))
        tests += int(stats["tests"]); prps += int(stats["prps"])
        if tests > 100000:
            p, tests, prps = prps / tests, 0, 0
        st["exp_hits"] += scan.masses(hist, p, int(stats["T"]))[0]
        T[u] = scan.best_threshold(hist, p, t_sieve, t_test)[0]
        for k in ks:
            res = search.verify_success(s, k)
            if res is None:
                print(f"  !! {s['name']} k={k} reported by tscan but REJECTED by verify_success", flush=True)
                continue
            res["name"] = s["name"]
            st["found"].append(res)
            print(f"  SUCCESS {s['name']} k={k} N={res['N']} ({res['digits']} digits) g={res['g']}", flush=True)
        pos[s["name"]] = k0 + chunk
        calls += 1
        if calls % 5 == 0 or ks:
            st["seconds"] += time.time() - t_start
            t_start = time.time()
            save()
    st["seconds"] += time.time() - t_start
    save()
    lo = min(pos[s["name"]] for s in order)
    print(f"== {len(order)} progressions at k >= {lo:,}; expected hits {st['exp_hits']:.3f}; {st['seconds']:.0f}s; "
          f"found {sorted(st['found'], key=lambda f: int(f['N']))[:3]}", flush=True)


if __name__ == "__main__":
    main()

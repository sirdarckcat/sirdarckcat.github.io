#!/usr/bin/env python3
"""Chunked, resumable driver for tscan.c (the small-N threshold scanner).

    python3 scan.py plan.json <seconds>

plan.json is a list of jobs:
  {"spec": path to a cover.py output with a "name" field,
   "kcap": stop at this k,  "budget_s": seconds allowed for this job,
   optional "B" (sieve bound, default 131072), "logK" (log2 of the block
   size, default 18), "chunk_s" (target seconds per chunk, default 240),
   "T" (fixed selection threshold; otherwise chosen after every chunk)}

For each job the driver scans N = N0 + k*M upward from the saved position
until a success, the cap, the job's budget or the overall deadline.  State
is kept next to the spec in <spec>.state.json:
  {"next_k", "seconds", "found", "exp_hits"}
exp_hits is the expected number of successes among the k tested so far,
computed from the survivor histogram tscan prints: a k with a survivors
succeeds with probability (1 - p)^a.

tscan only tests the k with at most T survivors.  T is the value that
maximises (share of expected hits kept) / (time per k), from the last
chunk's histogram, the measured chance p that a survivor is prime and the
two timings measured by a short calibration (sieve per k, one Fermat test).

Every k that tscan reports is re-checked here with search.verify_success
(BPSW on N - q for every prime q < Q), which also computes g(N).  The
record itself is then proved by package_record.py and PARI, with no
reference to this scanner.
"""
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import search  # noqa: E402

THREADS = int(os.environ.get("OMP_NUM_THREADS", os.cpu_count()))


def build(nl):
    """Compile tscan.c for nl 64-bit limbs unless an up-to-date binary exists."""
    exe, src = os.path.join(HERE, f"tscan{nl}"), os.path.join(HERE, "tscan.c")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        subprocess.run(["gcc", "-O3", "-march=native", "-fopenmp", f"-DNL={nl}", "-o", exe + ".tmp", src],
                       check=True)
        os.replace(exe + ".tmp", exe)
    return exe


def first_k(spec):
    """Smallest k tscan accepts.  It refuses N below 2^39: its sieve takes for granted that every
    N - q is larger than every sieve prime.  Nothing is lost: g(N) <= 9,781 is known for N <= 4*10^18."""
    N0, M = int(spec["N0"]), int(spec["M"])
    return max(0, -((N0 - (1 << 40)) // M))


def write_job(spec, path):
    with open(path, "w") as f:
        f.write(f"{int(spec['N0']):x}\n{int(spec['M']):x}\n{len(spec['residual'])}\n")
        f.write(" ".join(str(int(q)) for q in spec["residual"]) + "\n")


def scan(exe, jobfile, k0, k1, B, logK, T):
    out = subprocess.run([exe, jobfile, str(k0), str(k1), str(B), str(logK), str(T)],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    st = dict(kv.split("=") for kv in [l for l in out if l.startswith("STATS")][0].split()[1:])
    hist = {int(a): int(c) for a, c in (x.split(":") for x in st["hist"].split(","))}
    return st, hist, sorted(int(l.split()[1]) for l in out if l.startswith("S "))


def masses(hist, p, T):
    """(expected hits among the k with a <= T, expected hits among all k)"""
    return (sum(c * (1 - p) ** a for a, c in hist.items() if a <= T),
            sum(c * (1 - p) ** a for a, c in hist.items()))


def best_threshold(hist, p, t_sieve, t_test):
    """T maximising share / time-per-k.  Returns (T, k per second at that T)."""
    tot, all_mass = sum(hist.values()), masses(hist, p, 255)[1]
    best, m, tests = None, 0.0, 0.0
    for a in sorted(hist):
        m += hist[a] * (1 - p) ** a
        tests += hist[a] * (1 - (1 - p) ** a) / p          # expected tests until the first prime
        cost = t_sieve + tests / tot * t_test
        if best is None or (m / all_mass) / cost > best[1]:
            best = (a, (m / all_mass) / cost, 1 / cost)
    return best[0], best[2]


def calibrate(exe, jobfile, k0, B, logK):
    """Wall-clock seconds per k for the sieve alone and per Fermat test; p; histogram."""
    K = 1 << logK
    n0, n1 = 16 * K * THREADS, 2 * K * THREADS
    st0, hist, _ = scan(exe, jobfile, k0, k0 + n0, B, logK, -1)
    t_sieve = float(st0["seconds"]) / n0
    st1, _, _ = scan(exe, jobfile, k0, k0 + n1, B, logK, 255)
    p = int(st1["prps"]) / int(st1["tests"])
    t_test = max(float(st1["seconds"]) / n1 - t_sieve, 1e-12) * n1 / int(st1["tests"])
    return t_sieve, t_test, p, hist


def main():
    plan = json.load(open(sys.argv[1]))
    deadline = time.time() + float(sys.argv[2])
    for job in plan:
        spec = json.load(open(job["spec"]))
        spec = spec[0] if isinstance(spec, list) else spec
        stem = job["spec"][:-5]
        st = {"next_k": 0, "seconds": 0.0, "found": None, "exp_hits": 0.0}
        if os.path.exists(stem + ".state.json"):
            st.update(json.load(open(stem + ".state.json")))
        B, logK, chunk_s = job.get("B", 131072), job.get("logK", 18), job.get("chunk_s", 240)
        write_job(spec, stem + ".job")
        nl = ((int(spec["N0"]) + job["kcap"] * int(spec["M"])).bit_length() + 1 + 63) // 64
        exe = build(nl)
        cal = None
        while (not st["found"] and st["next_k"] < job["kcap"] and st["seconds"] < job["budget_s"]
               and time.time() + 1.5 * chunk_s < deadline):
            t0 = time.time()
            if cal is None:
                t_sieve, t_test, p, hist = cal = calibrate(exe, stem + ".job", max(st["next_k"], first_k(spec)),
                                                           B, logK)
                T, rate = best_threshold(hist, p, t_sieve, t_test)
                print(f"  calibration at k={st['next_k']}: sieve {t_sieve * 1e9:.1f} ns/k, Fermat test "
                      f"{t_test * 1e9:.0f} ns (wall clock, {THREADS} threads), p={p:.3f}", flush=True)
            T = job.get("T", T)
            k0 = max(st["next_k"], first_k(spec))
            k1 = min(k0 + (max(1, int(rate * chunk_s) >> logK) << logK), job["kcap"])
            stats, hist, ks = scan(exe, stem + ".job", k0, k1, B, logK, T)
            st["seconds"] += time.time() - t0
            if int(stats["tests"]) > 1000:
                p = int(stats["prps"]) / int(stats["tests"])
            sel, tot = masses(hist, p, T)
            st["exp_hits"] += sel
            print(f"[{spec['name']}] k=[{k0},{k1}) {stats['seconds']}s ({(k1 - k0) / float(stats['seconds']) / 1e6:.2f} M k/s) "
                  f"T={T}: tested {100 * int(stats['selected']) / (k1 - k0):.2f}% of k holding {100 * sel / tot:.1f}% "
                  f"of the hits, E={-math.log(tot / (k1 - k0)):.2f}, expected hits so far {st['exp_hits']:.2f}, "
                  f"reported {stats['found']}", flush=True)
            T, rate = best_threshold(hist, p, t_sieve, t_test)
            for k in ks:
                res = search.verify_success(spec, k)
                if res is None:
                    print(f"  !! k={k} reported by tscan but REJECTED by verify_success", flush=True)
                    continue
                res["name"] = spec["name"]
                with open(stem + ".found.jsonl", "a") as f:
                    f.write(json.dumps(res) + "\n")
                print(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} g={res['g']}", flush=True)
                st["found"] = st["found"] or res
            if not st["found"]:
                st["next_k"] = k1
            json.dump(st, open(stem + ".state.json", "w"))
        print(f"== {spec['name']}: next_k={st['next_k']:,} seconds={st['seconds']:.0f} "
              f"expected hits {st['exp_hits']:.2f} found={st['found']}", flush=True)


if __name__ == "__main__":
    main()

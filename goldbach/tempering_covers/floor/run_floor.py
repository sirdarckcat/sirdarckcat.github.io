# Where do complete covers END? For each x of T2, ln g0(Q) = ln(number of complete covers of the odd primes below Q by the
# odd primes up to x) from the research session's cover_floor (copied here from ccr-d4a17dd0-7uu03r, goldbach/sublinear,
# commit 29b8903), at four targets, about 60%, 75%, 85% and 93% of the tempered reach, two seeds each; then the straight-line
# end Q + ln g0(Q) / |slope| from the last interval.  Runs are single-threaded (OMP_NUM_THREADS=1: the result does not depend
# on the thread count, and one thread does not spin on a shared machine), several at a time; a run whose output exists is skipped.
#   python3 run_floor.py run [procs] [x ...]      the runs
#   python3 run_floor.py report [x ...]           ln g0 per target and seed, slopes, ends (floor_report.md, floor_points.json)
import json, math, os, subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); T2 = os.path.dirname(HERE)
sys.path.insert(0, T2)
from reach import first_unstruck
XS = (127, 149, 251, 349, 397, 599)
FRACS = (0.60, 0.75, 0.85, 0.93)
SEEDS = (1, 2)
SWEEPS, BURN = 400000, 100000

def tempered_reach():
    """x -> (reach of the best tempered vector, the Q it was found at), from t2_runs.jsonl (every run, probes included)"""
    best = {}
    for l in open(os.path.join(T2, "t2_runs.jsonl")):
        r = json.loads(l)
        if r["k"] == 0 and (r["x"] not in best or r["Q"] > best[r["x"]]["Q"]): best[r["x"]] = r
    return {x: (first_unstruck([tuple(map(int, t.split(":"))) for t in r["best"].split()]), r["Q"]) for x, r in best.items()}

def targets(reach): return [int(round(f * reach)) for f in FRACS]

def out_name(x, Q, s): return os.path.join(HERE, "runs", f"out_x{x}_Q{Q}_s{s}.txt")

def one(job):
    x, Q, s, Y = job
    out = out_name(x, Q, s)
    if os.path.exists(out): return out
    tmp = out + ".part"
    log = open(out.replace(".txt", ".log"), "w")
    subprocess.run([os.path.join(HERE, "cover_floor"), str(Q), f"odd<={x}", os.path.join(HERE, "cover_floor_betas_deep.txt"), str(SWEEPS), str(BURN), tmp, str(s)],
                   env=dict(os.environ, OMP_NUM_THREADS="1", COVER_FLOOR_REACH=str(Y)), stdout=log, stderr=subprocess.STDOUT, check=True)
    os.rename(tmp, out); print(f"done x={x} Q={Q} seed={s}", flush=True)
    return out

def reach_points(paths):
    """run cover_floor.py --reach on the given outputs; returns [(y, ln g0, samples beyond, path)]"""
    txt = subprocess.run([sys.executable, os.path.join(HERE, "cover_floor.py"), "--reach"] + paths, capture_output=True, text=True, check=True).stdout
    pts = []
    for line in txt.splitlines():
        m = re.match(r"\s+(\d+)\s+(-?[\d.]+)\s+(\d*)\s+(\S+)$", line)
        if m: pts.append((int(m.group(1)), float(m.group(2)), int(m.group(3)) if m.group(3) else 0, m.group(4)))
    return txt, pts

if __name__ == "__main__":
    mode = sys.argv[1]
    R = tempered_reach()
    if mode == "run":
        procs = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        xs = [int(a) for a in sys.argv[3:]] or list(XS)
        os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
        jobs = [(x, Q, s, 2 * R[x][0]) for x in xs for Q in targets(R[x][0]) for s in SEEDS]
        with ThreadPoolExecutor(procs) as ex: list(ex.map(one, jobs))
    elif mode == "report":
        xs = [int(a) for a in sys.argv[2:]] or list(XS)
        rep, allpts = [], {}
        for x in xs:
            reach, Qr = R[x]; Qs = targets(reach)
            paths = [out_name(x, Q, s) for Q in Qs for s in SEEDS if os.path.exists(out_name(x, Q, s))]
            if not paths: continue
            txt, pts = reach_points(paths)
            at = {}                                     # (Q, seed) -> ln g0(Q) from that run's own target
            for y, v, c, p in pts:
                m = re.search(r"_Q(\d+)_s(\d+)\.txt$", p)
                if m and int(m.group(1)) == y and c == 0: at[(y, int(m.group(2)))] = v
            mean = {Q: sum(at[(Q, s)] for s in SEEDS if (Q, s) in at) / max(1, sum((Q, s) in at for s in SEEDS)) for Q in Qs if any((Q, s) in at for s in SEEDS)}
            Qd = sorted(mean); slope = end = None
            if len(Qd) >= 2:
                q1, q2 = Qd[-2], Qd[-1]; slope = (mean[q2] - mean[q1]) / (q2 - q1) * 1000
                end = q2 + mean[q2] / (-slope / 1000) if slope < 0 else None
            tail = [(y, v, c) for y, v, c, p in pts if c > 0 and p.endswith(f"_Q{Qd[-1]}_s1.txt")] if Qd else []
            allpts[x] = dict(reach=reach, Q_found=Qr, targets=Qs, ln_g0={f"{Q}:{s}": at[(Q, s)] for (Q, s) in sorted(at)},
                             slope_per_1000=slope, straight_end=end, tail_last_target_seed1=tail)
            rep.append(f"### x = {x:,}: tempered reach {reach:,} (vector found at Q = {Qr:,})\n")
            rep.append("| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |")
            rep.append("|---|---|---|---|---|")
            for Q in Qs:
                v = [f"{at[(Q, s)]:.2f}" if (Q, s) in at else "–" for s in SEEDS]
                rep.append(f"| {Q:,} | {Q / reach:.2f} | {v[0]} | {v[1]} | {mean[Q]:.2f} |" if Q in mean else f"| {Q:,} | {Q / reach:.2f} | {v[0]} | {v[1]} | – |")
            if slope is not None:
                rep.append(f"\nSlope of the last interval: {slope:.2f} per 1,000. Straight-line end: " + (f"{end:,.0f} ({end / reach:.3f} × the tempered reach)." if end else "none (not falling)."))
            if tail:
                rep.append(f"Tail of the {Qd[-1]:,} run (seed 1): ln g0 = " + ", ".join(f"{v:.1f} at {y:,}" for y, v, c in tail[::max(1, len(tail) // 6)]) + ".")
            rep.append("")
        open(os.path.join(HERE, "floor_report.md"), "w").write("\n".join(rep) + "\n")
        json.dump(allpts, open(os.path.join(HERE, "floor_points.json"), "w"), indent=1)
        print("\n".join(rep))

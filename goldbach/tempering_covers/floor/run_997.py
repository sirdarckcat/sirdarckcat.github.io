# x = 997 (167 moduli) near the end of complete covers, as the research session asked (24 Nov 18:45 UTC):
# targets Q = 39,000 and 40,111; two seeds each, (a) started from the best cover known (complete to 40,111) and (b) from random
# vectors; 400,000 sweeps, burn 100,000, COVER_FLOOR_REACH = 47,000; cover_floor2 keeps the vector of the largest reach seen.
#   python3 run_997.py run [procs]      the runs (start-cover runs first; outputs that exist are skipped)
#   python3 run_997.py report           ln g0 per run, drift of the quarters, the largest reaches seen (rechecked), x997_report.md
import os, re, subprocess, sys, json
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); T2 = os.path.dirname(HERE)
sys.path.insert(0, T2)
from reach import first_unstruck
START = os.path.join(T2, "complete_cover_40111_167primes.txt")
TARGETS, SEEDS, Y = (39000, 40111), (1, 2), 47000
SWEEPS, BURN = int(os.environ.get("X997_SWEEPS", 400000)), int(os.environ.get("X997_BURN", 100000))

def name(Q, s, start, sweeps=SWEEPS):
    tag = "" if sweeps == 400000 else f"_w{sweeps // 1000}k"
    return os.path.join(HERE, "runs", f"out_x997_Q{Q}_s{s}{'_start' if start else ''}{tag}.txt")

def one(job):
    Q, s, start = job
    out = name(Q, s, start)
    if os.path.exists(out): return out
    cmd = [os.path.join(HERE, "cover_floor2"), str(Q), "odd<=997", os.path.join(HERE, "cover_floor_betas_deep.txt"), str(SWEEPS), str(BURN), out + ".part", str(s)]
    if start: cmd.append(START)
    with open(out.replace(".txt", ".log"), "w") as log:
        subprocess.run(cmd, env=dict(os.environ, OMP_NUM_THREADS="1", COVER_FLOOR_REACH=str(Y)), stdout=log, stderr=subprocess.STDOUT, check=True)
    os.rename(out + ".part", out); print(f"done Q={Q} seed={s} {'start' if start else 'random'}", flush=True)
    return out

def best_lines(path):
    """the records printed to the run's log (each new largest reach), and the final BESTREACH of the output"""
    recs = []
    log = path.replace(".txt", ".log")
    if os.path.exists(log):
        for line in open(log):
            m = re.match(r"new largest reach (\d+) at sweep (\d+), beta ([\d.]+): (.*)$", line)
            if m: recs.append((int(m.group(1)), int(m.group(2)), float(m.group(3)), m.group(4)))
    return recs

if __name__ == "__main__":
    if sys.argv[1] == "run":
        procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
        jobs = [(Q, s, True) for Q in TARGETS for s in SEEDS] + [(Q, s, False) for Q in TARGETS for s in SEEDS]
        with ThreadPoolExecutor(procs) as ex: list(ex.map(one, jobs))
    else:
        rows, best = [], []
        for Q in TARGETS:
            for start in (True, False):
                for s in SEEDS:
                    p = name(Q, s, start)
                    if not os.path.exists(p): continue
                    txt = subprocess.run([sys.executable, os.path.join(HERE, "cover_floor.py"), "--reach", p], capture_output=True, text=True).stdout
                    m = re.search(r"ln g0\((\d+)\) = ([-\d.]+); (\d+) samples of complete covers, reach up to (\d+)", txt)
                    q = subprocess.run([sys.executable, os.path.join(HERE, "cover_floor.py"), p], capture_output=True, text=True).stdout
                    cold = [l for l in q.splitlines() if re.match(r"\s+\d+\.\d+\s", l)][-3:]          # the three coldest temperatures: quarters of the run
                    b = [l for l in open(p) if l.startswith("BESTREACH")]
                    if b:
                        t = b[0].split(); pairs = [tuple(map(int, w.split(":"))) for w in t[5:]]
                        chk = first_unstruck(pairs); best.append((chk, int(t[1]), p, " ".join(t[5:]), sum(1 for _, a in pairs if a == 0)))
                    rows.append((Q, "start" if start else "random", s, float(m.group(2)) if m else float("nan"), int(m.group(3)) if m else 0, int(m.group(4)) if m else 0, cold))
        out = ["| Q | start | seed | ln g0(Q) | complete-cover samples | largest reach sampled |", "|---|---|---|---|---|---|"]
        for Q, st, s, v, n, rr, _ in rows: out.append(f"| {Q:,} | {st} | {s} | {v:.2f} | {n:,} | {rr:,} |")
        out.append("\nDrift: mean k in the four quarters of each run at the three coldest temperatures (columns: beta, <k>, sd, lowest, quarters ...)")
        for Q, st, s, v, n, rr, cold in rows:
            out.append(f"- Q = {Q:,}, {st}, seed {s}:"); out += ["    " + c.strip() for c in cold]
        best.sort(reverse=True)
        out.append("\nLargest reaches seen (rechecked with reach.py's first_unstruck; zero classes counted):")
        for chk, rep, p, vec, z in best: out.append(f"- {os.path.basename(p)}: reach {rep:,} (recheck {chk:,}){', ' + str(z) + ' zero classes' if z else ''}")
        if best and best[0][0] > 40111:
            out.append(f"\nNew best cover on the 167 odd primes up to 997: first odd prime in no class {best[0][0]:,}\n{best[0][3]}")
        open(os.path.join(HERE, "x997_report.md"), "w").write("\n".join(out) + "\n"); print("\n".join(out))

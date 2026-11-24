# For each finished x of T2: rerun, with ptcover_fast2, the runs at the two ends of the bracket that were made before it existed
# (the seeds that reached k = 0 at the largest Q, and every long run at the smallest Q missed), to get the first sweep at which
# each reached its best k. ptcover_fast2 makes the same run as ptcover_fast (same random numbers, same moves), so k and BEST
# must come out identical to the logged run; that is checked and recorded. Results go to t2_firsthit.jsonl (resumable).
#   python3 t2_firsthit.py [procs]
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "t2_firsthit.jsonl")

def finished():
    """x -> (largest Q reached, smallest Q missed by all seeds), from the search's own summary lines in t2.log"""
    br = {}
    for line in open(os.path.join(HERE, "t2.log")):
        m = re.match(r"x=(\d+): largest Q reached (\d+), smallest Q missed by all seeds (\d+)", line)
        if m: br[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return br

def key(r): return (r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))

def rerun(r):
    mod = os.path.join(HERE, r.get("start") or f"mod_{r['x']}.txt")
    t0 = time.time()
    out = subprocess.run([os.path.join(HERE, "ptcover_fast2"), str(r["Q"]), mod, str(r["sweeps"]), str(r["seed"]), os.path.join(HERE, "betas56.txt")],
                         capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1")).stdout
    k = int(re.search(r"# best k found: (\d+)", out).group(1))
    best = re.search(r"^BEST (.*)$", out, re.M).group(1).strip()
    fl = re.search(r"^# first sweep with best k <= j \(j:sweep\):(.*)$", out, re.M).group(1)
    first = {int(a): int(b) for a, b in (t.split(":") for t in fl.split())}
    rec = dict(x=r["x"], Q=r["Q"], seed=r["seed"], sweeps=r["sweeps"], start=r.get("start", ""), k=k, first_le=first,
               identical=(k == r["k"] and best == r["best"]), seconds=round(time.time() - t0))
    with open(OUT, "a") as f: f.write(json.dumps(rec) + "\n")
    print(f"x={rec['x']} Q={rec['Q']} seed={rec['seed']}: k {k}, first sweep at best k {first.get(k)}, identical {rec['identical']} ({rec['seconds']} s)", flush=True)
    return rec

if __name__ == "__main__":
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    runs = [json.loads(l) for l in open(os.path.join(HERE, "t2_runs.jsonl"))]
    have = {key(json.loads(l)) for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = []
    for x, (lo, hi) in sorted(finished().items()):
        for r in runs:
            if r["x"] != x or "first_le" in r or key(r) in have: continue
            if (r["Q"] == lo and r["k"] == 0) or (r["Q"] == hi and r["sweeps"] >= 80000):
                todo.append(r); have.add(key(r))
    print(f"{len(todo)} reruns", flush=True)
    with ThreadPoolExecutor(procs) as ex:
        list(ex.map(rerun, todo))

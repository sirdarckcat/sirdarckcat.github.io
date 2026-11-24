# T2: the largest Q at which parallel tempering finds a complete cover of the odd primes below Q, for the odd primes up to x.
# Bisection on Q with 4 seeds per point (one per core, OMP_NUM_THREADS=1), at least 80,000 sweeps; a point counts as reached
# when some seed ends with best k = 0. Every run is appended to t2_runs.jsonl (resumable: a run already logged is not redone).
#   python3 t2.py x [x ...]
import subprocess, json, math, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "t2_runs.jsonl")
SEEDS = (1, 2, 3, 4)

def sweeps_for(x):
    return 80000 if x <= 400 else 120000 if x <= 800 else 160000

def logged():
    runs = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            r = json.loads(line); runs[(r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))] = r
    return runs

def one(x, Q, seed, sweeps, start=""):
    key = (x, Q, seed, sweeps, start)
    if key in DONE: return DONE[key]
    mod = os.path.join(HERE, start or f"mod_{x}.txt")
    t0 = time.time()
    out = subprocess.run([os.path.join(HERE, "ptcover_fast"), str(Q), mod, str(sweeps), str(seed), os.path.join(HERE, "betas56.txt")],
                         capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1")).stdout
    k = int(re.search(r"# best k found: (\d+)", out).group(1))
    best = re.search(r"^BEST (.*)$", out, re.M).group(1).strip()
    r = dict(x=x, Q=Q, seed=seed, sweeps=sweeps, start=start, k=k, best=best, seconds=round(time.time() - t0))
    with open(LOG, "a") as f: f.write(json.dumps(r) + "\n")
    DONE[key] = r
    print(f"  x={x} Q={Q} seed={seed} sweeps={sweeps}{' start=' + start if start else ''}: best k {k}  ({r['seconds']} s)", flush=True)
    return r

def point(x, Q, sweeps, start=""):
    with ThreadPoolExecutor(len(SEEDS)) as ex:
        rs = list(ex.map(lambda s: one(x, Q, s, sweeps, start), SEEDS))
    return rs

def search(x, lo=None, hi=None, start=""):
    L = math.log(x); S = sweeps_for(x)
    if lo is None and hi is None:
        q0 = 0.87 * x * L * L
        with ThreadPoolExecutor(4) as ex:                    # coarse scan, one seed, short runs: only a hint
            coarse = list(ex.map(lambda f: one(x, int(q0 * f), 1, 20000, start), (0.90, 0.96, 1.02, 1.08)))
        ok = [r["Q"] for r in coarse if r["k"] == 0]; bad = [r["Q"] for r in coarse if r["k"] > 0]
        if ok: lo = max(ok)
        else:                                                 # nothing reached: go down until a long run reaches
            lo = int(q0 * 0.85)
            while not any(r["k"] == 0 for r in point(x, lo, S, start)): lo = int(lo * 0.92)
        hi = min([q for q in bad if q > lo], default=int(lo * 1.1))
    # hi must fail with long runs on all seeds; if a seed reaches it, move up
    while True:
        rs = point(x, hi, S, start)
        if any(r["k"] == 0 for r in rs): lo, hi = hi, int(hi * 1.05)
        else: break
    while hi - lo > max(40, lo // 200):                       # resolution 0.5%
        mid = (lo + hi) // 2
        rs = point(x, mid, S, start)
        if any(r["k"] == 0 for r in rs): lo = mid
        else: hi = mid
    print(f"x={x}: largest Q reached {lo}, smallest Q missed by all seeds {hi}", flush=True)
    return lo, hi

if __name__ == "__main__":
    DONE = logged()
    args = sys.argv[1:]
    for a in args:
        if ":" in a:                                          # x:lo:hi[:startfile] for a search from a known bracket
            p = a.split(":"); search(int(p[0]), int(p[1]), int(p[2]), p[3] if len(p) > 3 else "")
        else:
            search(int(a))

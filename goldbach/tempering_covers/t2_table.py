# Table of T2 from t2_runs.jsonl and the search's brackets in t2.log; the reach of each best vector is rechecked by reach.py.
#   python3 t2_table.py > t2_table.md     (also writes t2_vectors.txt)
# Columns: the bracket of the search at its planned budget (sweeps_for(x) in t2.py), the seeds that reached k = 0 at the top of the
# bracket and the sweep at which each first did, the best k of each seed at the bottom of the miss and the sweep at which it was first
# reached, then the 4x longer runs at that same missed Q (t2_probe.py) where they were made, and the reach of the best vector of any run.
import json, math, os, re, sys
from reach import first_unstruck
import t2
runs = [json.loads(l) for l in open("t2_runs.jsonl")]
FH = {}
for r in runs:
    if "first_le" in r: FH[(r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))] = {int(a): b for a, b in r["first_le"].items()}
if os.path.exists("t2_firsthit.jsonl"):
    for l in open("t2_firsthit.jsonl"):
        r = json.loads(l)
        if r["identical"]: FH[(r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))] = {int(a): b for a, b in r["first_le"].items()}
def fh(r):
    v = FH.get((r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))); return None if v is None else v.get(r["k"])
def fmt(r): s = fh(r); return f"{r['k']} ({s:,})" if s is not None else f"{r['k']} (–)"
br = {}
for line in open("t2.log"):
    m = re.match(r"x=(\d+): largest Q reached (\d+), smallest Q missed by all seeds (\d+)", line)
    if m: br[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
print("| x | moduli | sweeps per run | bracket at that budget: largest Q reached / smallest Q missed by all seeds | seeds at k = 0 at the top (sweep of the first k = 0) | "
      "best k of each seed at the miss (sweep it was first reached) | 4× longer runs at the miss: best k (sweep) | best vector of any run: first odd prime in no class | / (x ln x) | / (x ln² x) | runs |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
vec = {}
for x in sorted({r["x"] for r in runs}):
    R = [r for r in runs if r["x"] == x]; S = t2.sweeps_for(x); L = math.log(x)
    ok = [r for r in R if r["k"] == 0]
    if not ok: continue
    best = max(ok, key=lambda r: r["Q"]); pairs = [tuple(map(int, t.split(":"))) for t in best["best"].split()]
    reach = first_unstruck(pairs); vec[x] = (reach, best)
    if x in br:
        lo, hi = br[x]
        top = sorted((r for r in R if r["Q"] == lo and r["k"] == 0 and r["sweeps"] == S), key=lambda r: r["seed"])
        top_s = ", ".join(f"{r['seed']} ({fh(r):,})" if fh(r) is not None else f"{r['seed']} (–)" for r in top) or "coarse scan only"
        miss = sorted((r for r in R if r["Q"] == hi and r["sweeps"] == S), key=lambda r: r["seed"])
        prob = sorted((r for r in R if r["Q"] == hi and r["sweeps"] == 4 * S), key=lambda r: r["seed"])
        prob_s = ", ".join(fmt(r) for r in prob) if prob else "–"
        brs = f"{lo:,} / {hi:,}"
    else:
        brs, top_s, prob_s = "search running", "", ""; miss = []
    print(f"| {x:,} | {len(pairs)} | {S:,} | {brs} | {top_s} | {', '.join(fmt(r) for r in miss)} | {prob_s} | {reach:,} (Q = {best['Q']:,}, {best['sweeps']:,} sweeps) | "
          f"{reach / (x * L):.2f} | {reach / (x * L * L):.3f} | {len(R)} |")
with open("t2_vectors.txt", "w") as f:
    for x, (reach, best) in vec.items():
        f.write(f"# odd primes up to {x}: every odd prime below {reach:,} lies in the class of some modulus (first odd prime in no class: {reach}); "
                f"found by ptcover_fast at Q = {best['Q']}, seed {best['seed']}, {best['sweeps']} sweeps; rechecked by reach.py\n{best['best']}\n")

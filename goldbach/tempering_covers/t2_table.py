# Table of the largest Q reached per x, from t2_runs.jsonl, with the reach of the best vector rechecked by reach.py.
import json, math, os, sys
from reach import first_unstruck
runs = [json.loads(l) for l in open("t2_runs.jsonl")]
xs = sorted({r["x"] for r in runs})
# first sweep at which a run reached each best k: logged directly by runs made with ptcover_fast2, or from t2_firsthit.py's reruns
FH = {}
for r in runs:
    if "first_le" in r: FH[(r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))] = (r["k"], {int(a): b for a, b in r["first_le"].items()}, True)
if os.path.exists("t2_firsthit.jsonl"):
    for l in open("t2_firsthit.jsonl"):
        r = json.loads(l); FH[(r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", ""))] = (r["k"], {int(a): b for a, b in r["first_le"].items()}, r["identical"])
def fh(r):
    v = FH.get((r["x"], r["Q"], r["seed"], r["sweeps"], r.get("start", "")))
    return None if v is None else v[1].get(r["k"])
print("| primes up to x | moduli | largest Q reached | first odd prime in no class | / (x ln x) | / (x ln² x) | Q missed by all seeds (long runs) | sweeps per run | seeds at k = 0 (sweep of the first k = 0) | best k of each seed at the miss (sweep it was first reached) | runs |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
vec = {}
for x in xs:
    R = [r for r in runs if r["x"] == x]
    ok = [r for r in R if r["k"] == 0]
    if not ok: continue
    best = max(ok, key=lambda r: r["Q"])
    pairs = [tuple(map(int, t.split(":"))) for t in best["best"].split()]
    reach = first_unstruck(pairs)
    miss = [r["Q"] for r in R if r["k"] > 0 and r["Q"] > best["Q"] and r["sweeps"] >= 80000]
    missQ = min((q for q in set(miss) if all(rr["k"] > 0 for rr in R if rr["Q"] == q and rr["sweeps"] >= 80000)), default=None)
    L = math.log(x)
    hits = sorted((r for r in ok if r["Q"] == best["Q"] and r["sweeps"] >= 80000), key=lambda r: r["seed"])
    hit_s = ", ".join(f"{r['seed']} ({fh(r):,})" if fh(r) is not None else f"{r['seed']} (–)" for r in hits)
    mr = sorted((r for r in R if missQ is not None and r["Q"] == missQ and r["sweeps"] >= 80000), key=lambda r: r["seed"])
    miss_s = ", ".join(f"{r['k']} ({fh(r):,})" if fh(r) is not None else f"{r['k']} (–)" for r in mr)
    sw = sorted({r["sweeps"] for r in hits + mr})
    print(f"| {x:,} | {len(pairs)} | {best['Q']:,} | {reach:,} | {reach/(x*L):.2f} | {reach/(x*L*L):.3f} | {'' if missQ is None else f'{missQ:,}'} | "
          f"{'/'.join(f'{v:,}' for v in sw)} | {hit_s} | {miss_s} | {len(R)} |")
    vec[x] = (reach, best)
with open("t2_vectors.txt", "w") as f:
    for x, (reach, best) in vec.items():
        f.write(f"# odd primes up to {x}: every odd prime below {reach:,} lies in the class of some modulus (first odd prime in no class: {reach}); "
                f"found by ptcover_fast at Q = {best['Q']}, seed {best['seed']}, {best['sweeps']} sweeps; rechecked by reach.py\n{best['best']}\n")

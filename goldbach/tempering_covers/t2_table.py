# Table of the largest Q reached per x, from t2_runs.jsonl, with the reach of the best vector rechecked by reach.py.
import json, math, sys
from reach import first_unstruck
runs = [json.loads(l) for l in open("t2_runs.jsonl")]
xs = sorted({r["x"] for r in runs})
print("| primes up to x | moduli | largest Q reached | first odd prime in no class | / (x ln x) | / (x ln² x) | Q missed by all seeds (long runs) | runs |")
print("|---|---|---|---|---|---|---|---|")
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
    print(f"| {x:,} | {len(pairs)} | {best['Q']:,} | {reach:,} | {reach/(x*L):.2f} | {reach/(x*L*L):.3f} | {'' if missQ is None else f'{missQ:,}'} | {len(R)} |")
    vec[x] = (reach, best)
with open("t2_vectors.txt", "w") as f:
    for x, (reach, best) in vec.items():
        f.write(f"# odd primes up to {x}: every odd prime below {reach:,} lies in the class of some modulus (first odd prime in no class: {reach}); "
                f"found by ptcover_fast at Q = {best['Q']}, seed {best['seed']}, {best['sweeps']} sweeps; rechecked by reach.py\n{best['best']}\n")

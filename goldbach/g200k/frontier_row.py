#!/usr/bin/env python3
"""The RESULTS.md row of a frontier rung (frontier.py or frontier_combine.py output), and its hits file.
    python3 frontier_row.py rung.json hits.txt"""
import json, math, sys
r = json.load(open(sys.argv[1]))
hits = sorted(r["hits"], key=lambda h: -h["closeness"])
pn = {49: 229, 51: 241, 53: 251, 55: 263, 57: 271, 59: 281}[r["moduli"]]
lnN = r["digits"] * math.log(10) - math.log(10) + math.log(r["c"][0] / r["c"][1]) / 2
p0 = math.exp(0.5772156649) * math.log(pn) / lnN
E = r["rows_min"] * -math.log(1 - p0)
c = r["c"][0] / r["c"][1]
rows = f"{r['rows_min']}" if r["rows_min"] == r["rows_max"] else f"{r['rows_min']}-{r['rows_max']}"
best = f"{hits[0]['closeness']:.4f} (g = {hits[0]['g']:,})" if hits else "-"
print(f"| {r['digits']} | {c:.7g} | {r['Q']:,} | {r['moduli']} | {r['covers']} | {rows} | {E:.1f} | {r['E_tested']:.2f} | {r['members']/1e9:.2f}G | "
      f"{r['tested']:,} | {r['p_hat']:.5f} | {r.get('skip', 0.98)} | {r['expected']:.2f} ({r['expected_lo']:.2f}-{r['expected_hi']:.2f}) | "
      f"{r['found']} | {r['found']/r['expected']:.2f} | {r['cpu_seconds']/3600:.2f} | {best} |")
with open(sys.argv[2], "w") as f:
    f.write(f"# {r['digits']}-digit frontier hits: digits g closeness N\n")
    for h in hits:
        f.write(f"{h['digits']} {h['g']} {h['closeness']:.6f} {h['N']}\n")

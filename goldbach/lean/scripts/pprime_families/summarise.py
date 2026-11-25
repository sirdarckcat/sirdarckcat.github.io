"""Tables from results.jsonl (run_all.py): one headline row per family and the full list of configurations.
The headline of a family is the configuration (work at least 10,000 units) that comes closest to the cover-first
prefix of equal work, measured on the members with at most 12 rows left at depth 200 (33,598 of them: the least noisy
of the counts)."""
import json, math, sys
import numpy as np
import pp
from refcurve import r1, cells

T = pp.TARGETS
def g(d, key="gain", f="{:+.2f}"):
    return " | ".join((f.format(d[key][str(t)] if str(t) in d[key] else d[key][t]) if math.isfinite(d[key].get(str(t), d[key].get(t, math.inf)) if isinstance(d[key], dict) else 0) else "-") for t in T)
def val(d, t):
    x = d.get(str(t), d.get(t)); return x if x is not None else math.inf
def row_cells(d, f):
    return " | ".join((f.format(val(d, t)) if math.isfinite(val(d, t)) else "-") for t in T)
def ratio(r, key):
    b = r["r2"][key]; return r[key] / b if b else float("nan")

rows = [json.loads(l) for l in open("results.jsonl")]
names = {"mitm": "meet in the middle, lists beyond the line only", "ktree": "four-list tree (Wagner), lists beyond the line only",
         "prefix": "meet in the middle as N = N1 + k M (best covers x lists beyond the line)", "bucket": "bucketing, tables of listed class tuples"}
out = []
out.append("## One row per family (the configuration closest to the cover-first prefix of equal work)\n")
out.append("| family | configuration | work, units | memory, entries | members put forward | successes among them | N examined for 1 | 3 | 10 | 30 | gain in nats over cover first at 1 | 3 | 10 | 30 "
           "| cover-first prefix of equal work, scored: successes | its gains at 1 | 3 | 10 | 30 | members with <= 10 rows left at depth 200: family / prefix of equal work / random sample of equal size | the same for <= 12 rows |")
out.append("|" + "---|" * 25)
heads = {}
for fam in ("mitm", "ktree", "prefix", "bucket"):
    rs = [r for r in rows if r["family"] == fam and r["work"] >= 10000]
    best = max(rs, key=lambda r: ratio(r, "le12")); heads[fam] = best
    for r in [best]:
        out.append(f"| {names[fam]} | {r['config']} | {r['work']:,.0f} | {r['memory']:,d} | {r['members']:,d} | {r['successes']} | {row_cells(r['examined'], '{:,.0f}')} | {row_cells(r['gain'], '{:+.2f}')} "
                   f"| {r['r2']['successes']} | {row_cells(r['r2']['gain'], '{:+.2f}')} | {r['le10']} / {r['r2']['le10']} / {r['random_expect']['le10']:.0f} | {r['le12']} / {r['r2']['le12']} / {r['random_expect']['le12']:.0f} |")
out.append("")
out.append("## Every configuration run\n")
for fam in ("mitm", "ktree", "prefix", "bucket"):
    rs = [r for r in rows if r["family"] == fam]
    out.append(f"### {names[fam]} ({len(rs)} configurations)\n")
    out.append("| configuration | generation, operations | generation, CPU s | memory, entries | members put forward | work, units | units of work per member put forward | successes (prefix of equal work) | <= 10 rows left at depth 200 (prefix of equal work; random) "
               "| <= 12 rows (prefix; random) | N examined for 1 | 3 | 10 | 30 | gain at 1 | 3 | 10 | 30 | prefix of equal work: gain at 1 | 3 | 10 | 30 | unscored, in cover-first order: gain at 1 | 3 | 10 | 30 |")
    out.append("|" + "---|" * 26)
    for r in rs:
        per = r["work"] / r["members"] if r["members"] else float("inf")
        out.append(f"| {r['config']} | {r['gen_ops']:,d} | {r['gen_cpu']:.2f} | {r['memory']:,d} | {r['members']:,d} | {r['work']:,.0f} | {per:,.2f} | {r['successes']} ({r['r2']['successes']}) "
                   f"| {r['le10']} ({r['r2']['le10']}; {r['random_expect']['le10']:.1f}) | {r['le12']} ({r['r2']['le12']}; {r['random_expect']['le12']:.0f}) | {row_cells(r['examined'], '{:,.0f}')} | {row_cells(r['gain'], '{:+.2f}')} "
                   f"| {row_cells(r['r2']['gain'], '{:+.2f}')} | {row_cells(r['gain_cover_order'], '{:+.2f}')} |")
    out.append("")
    # summary line: range of the capture ratio
    rr = [ratio(r, "le12") for r in rs if r["work"] >= 10000 and r["r2"]["le12"]]
    out.append(f"Share of the members with at most 12 rows left at depth 200 that the family captures, relative to the cover-first prefix of equal work: "
               f"{min(rr):.3f} to {max(rr):.3f} over the {len(rr)} configurations with at least 10,000 units of work (in nats: {("none captured" if min(rr) == 0 else format(math.log(min(rr)), "+.2f"))} to {math.log(max(rr)):+.2f}).\n")
open("table.md", "w").write("\n".join(out) + "\n")
print("\n".join(out[:8]))
for fam, r in heads.items():
    print(fam, "|", r["config"], "| le12 ratio", round(ratio(r, "le12"), 3), "| le10 ratio", round(ratio(r, "le10"), 3))

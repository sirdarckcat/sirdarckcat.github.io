"""Aggregate the per-runtime tallies (tally_rt.py output) into goldbach/phd/campaign3_gpu/TALLY.md and tally.json."""
import glob, json, os, sys, time
SP, OUT = sys.argv[1], sys.argv[2]
FAM = {"/content/c3g_g4": "Q = 122,000, 867-872 rows (v, w families), N < 10^199",
       "/content/c3g (search_gpu3.py, 867-row families)": "Q = 122,000, 867-872 rows (v, w families), N < 10^199",
       "/content/c3g (search_gpu2.py, full mass)": "Q = 122,000, 867-869 rows, search_gpu2.py at full mass, N < 10^199",
       "/content/c850": "Q = 122,000, 850-862 rows (Lean cover), N < 10^200",
       "/content/c140": "Q = 140,000, 1,011 rows (research cover), N < 10^200",
       "/content/c150": "Q = 150,000, 1,093-1,094 rows (research cover), N < 10^200"}
GPU = {"gold-g4": "RTX PRO 6000 (gold-g4)", "gold-g4b": "RTX PRO 6000 (gold-g4b)", "gold-g4c": "RTX PRO 6000 (gold-g4c)", "gold-a100": "A100 (gold-a100)",
       "gold-gpu": "L4 (gold-gpu)", "gold-gpu_c3g": "L4 (gold-gpu)", "gold-l4b": "L4 (gold-l4b)"}
rows = []
for f in sorted(glob.glob(SP + "/tally/gold-*.json")):
    gpu = GPU[os.path.basename(f)[:-5]]
    for d in json.load(open(f)):
        d["gpu"] = gpu; d["family"] = FAM.get(d["dir"], d["dir"]); rows.append(d)
fams = []
for r in rows:
    if r["family"] not in fams:
        fams.append(r["family"])
lines = ["# campaign3 on the GPUs: expected against found", "",
         f"Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. Regenerated from the runtimes' own logs:",
         "- `tally_rt.py` runs on each runtime and reads its search.log, gpu3_stats.log and found.jsonl;",
         "- this page is written from those results.", "",
         "Columns:",
         "- **members**: members scanned (sieved).",
         "- **hit mass**: members × hit% summed, i.e. the members' worth of full hit mass that was tested.",
         "- **expected**: the model's expected successes, measured on the members actually tested:",
         "  - *logged*: from `gpu3_stats.log`, Σ (1 − p^)^count over the tested members, p^ the batch's measured PRP rate;",
         "  - *model*: for slices from before that accounting (20:22-20:50 UTC), members × hit% × exp(−1.0275·E^ + 0.33) from each slice's own line. On the slices where both exist, this formula is within ~16% of the logged figure.",
         "- **found**: successes, each re-checked by `search.verify_success`; certified records are in `goldbach/records/`.", ""]
tot_e = tot_f = 0.0
summary = []
for fam in fams:
    rs = [r for r in rows if r["family"] == fam]
    lines += [f"## {fam}", "", "| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |", "|---|---|---|---|---|---|---|---|"]
    fe = ff = fm = fh = 0.0; gs = []
    for r in rs:
        e = r["expected_logged"] + r["expected_model"]
        lines.append(f"| {r['gpu']} | {r['slices']:,} | {r['members']/1e9:.2f}e9 | {r['hit_mass_members']/1e9:.3f}e9 | {r['mean_E']:.2f} | "
                     f"{e:.3f} ({r['expected_logged']:.3f} + {r['expected_model']:.3f}) | {r['found']} | {', '.join(f'{g:,}' for g in r['g']) or '-'} |")
        fe += e; ff += r["found"]; fm += r["members"]; fh += r["hit_mass_members"]; gs += r["g"]
    lines += [f"| **all** | | {fm/1e9:.2f}e9 | {fh/1e9:.3f}e9 | | **{fe:.3f}** | **{int(ff)}** | {', '.join(f'{g:,}' for g in sorted(gs, reverse=True)) or '-'} |", ""]
    tot_e += fe; tot_f += ff
    summary.append(dict(family=fam, members=fm, hit_mass_members=fh, expected=fe, found=int(ff), g=sorted(gs, reverse=True)))
lines += [f"**All covers: expected {tot_e:.2f}, found {int(tot_f)}.**", ""]
ov = os.path.join(OUT, "overshoot.json")
if os.path.exists(ov):
    o = json.load(open(ov))
    lines += ["## How far past Q the hits went (`overshoot.py`)", "",
              "The rows a hit survived beyond its threshold are the primes q in [Q, g) that its cover leaves uncovered. Each such N − q is",
              "a composite the cover did not force. The model makes each prime with probability p = boost / ln N, so the count is geometric",
              "with mean (1 − p)/p ≈ 41 and tail P(≥ u) = (1 − p)^u, and the sum over hits is negative binomial.", "",
              "| hit | Q | g | rows survived | expected | P(≥ that) |", "|---|---|---|---|---|---|"]
    for r in o["rows"]:
        lines.append(f"| `{r['name']}` | {r['Q']:,} | {r['g']:,} | {r['rows_survived']} | {r['expected']:.1f} | {r['tail']:.3f} |")
    lines.append("")
    for Q, b in o["by_Q"].items():
        lines.append(f"- Q = {int(Q):,}: {b['hits']} hits survived {b['rows_survived']} rows against {b['expected']} expected, P(sum ≥ that) = {b['tail']:.3f}.")
    lines.append("")
open(OUT + "/TALLY.md", "w").write("\n".join(lines))
json.dump(dict(updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), rows=rows, summary=summary), open(OUT + "/tally.json", "w"), indent=1)
print("\n".join(lines[-12:]))

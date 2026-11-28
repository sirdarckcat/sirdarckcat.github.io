# The final Q = 170,000 table of TALLY.md (26 Nov 08:39:40Z, the stop): round-1 and round-2 snapshot rows from ../../2026-11-25/tally_1025/snap_all.txt
# (c170, c170v, c170f: final since 23-24 Nov), and the last card of every c170r / c170g share from finals.txt (t3.py on the final snapshots; a resumed
# directory holds its predecessors' records, so these rows are whole shares). Copies of older directories inside later snapshots are not counted again
# (gold-l4d's c170f is gold-l4b's first 1,940 slices).   python3 mkmd_final.py
import json, os
H = os.path.dirname(os.path.abspath(__file__))
def load(fn):
    out = {}
    for l in open(fn):
        card, _, js = l.split(" ", 2)
        out[card] = {r["dir"]: r for r in json.loads(js)}
    return out
S = load(os.path.join(H, "../../2026-11-25/tally_1025/snap_all.txt")); F = load(os.path.join(H, "finals.txt"))
GPU = {"RTX": "RTX PRO 6000", "L4": "L4", "T4": "T4"}
T = dict(mem=0, hm=0.0, eh=0.0, sl=0)
def row(gpu, cards, r, note=""):
    T["mem"] += r["members"]; T["hm"] += r["hit_mass"]; T["eh"] += r["exp_hits"]; T["sl"] += r["slices"]
    f = [x for x in r["found"] if not x.get("near_miss")]
    print(f"| {GPU[gpu]} ({cards}) | {r['slices']:,} | {r['members']/1e9:.2f}e9 | {r['hit_mass']/1e9:.3f}e9 | {r['mean_E']:.2f} | {r['exp_hits']:.4f} | {len(f)} | {note} |")
print("| GPU (cards) | slices | members | hit mass | mean E^ | expected design hits (logged) | found | |")
print("|---|---|---|---|---|---|---|---|")
groups = [
 ("c170", "88-moduli covers, campaign mode, 23 Nov 03:55Z to 10:57Z (RTX) / 16:51Z (L4, T4)", [("RTX", "gold-g4"), ("RTX", "gold-g4b"), ("RTX", "gold-g4c"), ("L4", "gold-l4b"), ("L4", "gold-l4c"), ("T4", "gold-xt4")]),
 ("c170v", "89-moduli vectors, RTX vector mode, 23 Nov 10:26Z to 20:52Z", [("RTX", "gold-g4"), ("RTX", "gold-g4b"), ("RTX", "gold-g4c")]),
 ("c170f", "m88f family-B covers, campaign mode, 23 Nov 16:51Z to 24 Nov 00:44Z", [("L4", "gold-l4b"), ("L4", "gold-l4c"), ("T4", "gold-xt4")]),
]
for d, title, cards in groups:
    print(f"| **{d}**: {title} | | | | | | | |")
    for g, c in cards:
        row(g, c, S[c][d], "near-miss 158,209" if (c, d) == ("gold-g4c", "c170v") else "")
print("| **c170r**: 491-family vectors, RTX vector mode, top windows, 23 Nov 20:18Z to the stop (26 Nov 08:39:40Z) | | | | | | | |")
for p, cards, last, note in (("0", "gold-g4d → g4g → g4j", "gold-g4j", "near-miss 160,357 on gold-g4d; 2 calibration events"), ("1", "gold-g4e → g4h → g4k", "gold-g4k", "3 calibration events"),
                             ("2", "gold-g4f", "gold-g4f", "waited for a G4 from 24 Nov 19:59Z")):
    row("RTX", f"partition {p}: {cards}", F[last]["c170r"], note)
print("| **c170g**: top32-shifted m88f family-B, L4/T4 top levels, 23 Nov 20:20Z to 25 Nov 19:44Z | | | | | | | |")
for g, cards, last, note in (("L4", "gold-l4d → l4g → l4j", "gold-l4j", "stopped 25 Nov 19:43Z (G4s only)"), ("L4", "gold-l4e", "gold-l4e", "waited for an L4 from 24 Nov 22:39Z"),
                             ("L4", "gold-l4f → l4i", "gold-l4i", "stopped 25 Nov 19:44Z"), ("T4", "gold-xt4b → xt4c", "gold-xt4c", "stopped 25 Nov 19:42Z")):
    row(g, cards, F[last]["c170g"], note)
print(f"| **all logged** | {T['sl']:,} | {T['mem']/1e12:.2f}e12 | {T['hm']/1e12:.3f}e12 | | **{T['eh']:.3f}** | **0** | |")
nm = {}
def addn(d):
    for k, v in d.items(): nm[k] = nm.get(k, 0) + v
for c in ("gold-g4", "gold-g4b", "gold-g4c"):
    for d in ("c170", "c170v"):
        addn(S[c][d]["exp_near"])
for c in ("gold-g4j", "gold-g4k", "gold-g4f"):
    addn(F[c]["c170r"]["exp_near"])
print("near-misses expected by threshold (RTX, where logged):", {k: round(v, 4) for k, v in sorted(nm.items())})
print("since 25 Nov 19:55Z (the calibration):", {c: (round(F[c]["c170r"]["since"]["exp_hits"], 4), {k: round(v, 4) for k, v in F[c]["c170r"]["since"]["exp_near"].items()}, F[c]["c170r"]["since"]["slices"]) for c in ("gold-g4j", "gold-g4k")})

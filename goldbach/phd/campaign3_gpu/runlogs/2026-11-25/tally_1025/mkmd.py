import json
def load(fn):
    out = {}
    for l in open(fn):
        card, _, js = l.split(" ", 2)
        out[card] = {r["dir"]: r for r in json.loads(js)}
    return out
S = load("snap_all.txt"); L = load("lives_all.txt")
GPU = {"RTX": "RTX PRO 6000", "L4": "L4", "T4": "T4"}
T = dict(mem=0, hm=0.0, eh=0.0)
def row(gpu, cards, r, note=""):
    T["mem"] += r["members"]; T["hm"] += r["hit_mass"]; T["eh"] += r["exp_hits"]
    f = [x for x in r["found"] if not x.get("near_miss")]
    print(f"| {GPU[gpu]} ({cards}) | {r['slices']:,} | {r['members']/1e9:.2f}e9 | {r['hit_mass']/1e9:.3f}e9 | {r['mean_E']:.2f} | {r['exp_hits']:.4f} | {len(f)} | {note} |")
print("| campaign | GPU (cards) | slices | members | hit mass | mean E^ | expected design hits | found | |")
groups = [
 ("c170", "88-moduli covers, campaign mode, 23 Nov 03:55Z-10:57Z (RTX) / -16:51Z (L4, T4)", [("RTX", "gold-g4"), ("RTX", "gold-g4b"), ("RTX", "gold-g4c"), ("L4", "gold-l4b"), ("L4", "gold-l4c"), ("T4", "gold-xt4")]),
 ("c170v", "89-moduli vectors, RTX vector mode, 23 Nov 10:26Z-20:52Z", [("RTX", "gold-g4"), ("RTX", "gold-g4b"), ("RTX", "gold-g4c")]),
 ("c170f", "m88f family-B covers, campaign mode, 23 Nov 16:51Z-24 Nov 00:44Z", [("L4", "gold-l4b"), ("L4", "gold-l4c"), ("T4", "gold-xt4")]),
]
for d, title, cards in groups:
    print(f"| **{d}**: {title} | | | | | | | | |")
    for g, c in cards:
        row(g, c, S[c][d])
print("| **c170r**: 491-family vectors, RTX vector mode, top windows, since 23 Nov 20:18Z | | | | | | | | |")
for p, pre, live, note in (("0", "gold-g4d", "gold-g4g", "running"), ("1", "gold-g4e", "gold-g4h", "running"), ("2", "gold-g4f", None, "waits since 24 Nov 19:59Z")):
    r = L[live]["c170r"] if live else S[pre]["c170r"]
    row("RTX", f"partition {p}: {pre}" + (f" → {live}" if live else ""), r, note)
print("| **c170g**: top32-shifted m88f family-B (top3 first on gold-l4d), L4/T4 top levels, since 23 Nov 20:20Z | | | | | | | | |")
for g, pre, live, note in (("L4", "gold-l4d", "gold-l4g", "running"), ("L4", "gold-l4e", None, "waits since 24 Nov 22:39Z"), ("L4", "gold-l4f", "gold-l4i", "running"), ("T4", "gold-xt4b", "gold-xt4c", "running")):
    r = L[live]["c170g"] if live else S[pre]["c170g"]
    row(g, pre + (f" → {live}" if live else ""), r, note)
print(f"| **all logged** | | | {T['mem']/1e12:.2f}e12 | {T['hm']/1e12:.3f}e12 | | **{T['eh']:.3f}** | **0** | |")
# near-misses by threshold
nm = {}
for c, dd in list(S.items()):
    for d in ("c170", "c170v"):
        if c in ("gold-g4", "gold-g4b", "gold-g4c") and d in dd:
            for k, v in dd[d]["exp_near"].items(): nm[k] = nm.get(k, 0) + v
for live, pre in (("gold-g4g", None), ("gold-g4h", None)):
    for k, v in L[live]["c170r"]["exp_near"].items(): nm[k] = nm.get(k, 0) + v
for k, v in S["gold-g4f"]["c170r"]["exp_near"].items(): nm[k] = nm.get(k, 0) + v
print("near-misses expected by threshold:", {k: round(v, 4) for k, v in sorted(nm.items())}, "sum", round(sum(nm.values()), 4))
# own parts of the running cards
for live, pre, d in (("gold-g4g", "gold-g4d", "c170r"), ("gold-g4h", "gold-g4e", "c170r"), ("gold-l4g", "gold-l4d", "c170g"), ("gold-l4i", "gold-l4f", "c170g"), ("gold-xt4c", "gold-xt4b", "c170g")):
    r, p = L[live][d], S[pre][d]
    print(f"own {live}: slices {r['slices'] - p['slices']:,} members {(r['members'] - p['members'])/1e9:.2f}e9 exp {r['exp_hits'] - p['exp_hits']:.4f} near " +
          str({k: round(r['exp_near'].get(k, 0) - p['exp_near'].get(k, 0), 4) for k in sorted(set(r['exp_near']) | set(p['exp_near']))}) + f" last {r['last']}")
for c, d in (("gold-g4d", "c170r"), ("gold-g4e", "c170r"), ("gold-g4f", "c170r"), ("gold-l4d", "c170g"), ("gold-l4e", "c170g"), ("gold-l4f", "c170g"), ("gold-xt4b", "c170g")):
    r = S[c][d]; print(f"card {c} {d}: slices {r['slices']:,} exp {r['exp_hits']:.4f} near {({k: round(v, 4) for k, v in r['exp_near'].items()})} {r['first']}..{r['last']}")

import glob, json, math, os, re
# Per campaign directory on this runtime: slices, members, hit mass, E^, expected hits (logged per batch where
# gpu3_stats.log has it, else the model 2^20-slice estimate members * hit% * exp(-1.0275 E^ + 0.33)), found and g.
out = []
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) tests=(\d+) prp=(\d+) p\^=(\S+) alive/k=(\S+) E\^=(\S+) hit%=(\S+) found=(\d+)")
for d in ("/content/c3g_g4", "/content/c850", "/content/c140", "/content/c150", "/content/c160", "/content/c170"):   # /content/c3g (L4, seeded with July CPU lines) is tallied locally
    if not os.path.exists(d + "/search.log"):
        continue
    logged = {}                                         # slice name -> expected share of its batch
    if os.path.exists(d + "/gpu3_stats.log"):
        for l in open(d + "/gpu3_stats.log"):
            m = re.search(r"batch (\S+)\.\.(\S+) \((\d+) slices\).*expected hits ([\d.e+-]+)", l)
            if m:
                logged[m.group(2)] = (int(m.group(3)), float(m.group(4)))   # keyed by the batch's last slice
    rows, cur, seen = [], [], set()
    for l in open(d + "/search.log"):
        m = pat.match(l)
        if m:
            name, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            if name in seen:                                       # a slice logged twice (two processes for a few minutes, 23 Nov 03:07Z): count it once
                continue
            seen.add(name)
            rows.append(dict(name=name, k=b - a, tests=int(m.group(4)), prps=int(m.group(5)), E=float(m.group(8)), hit=float(m.group(9)) / 100))
    # attribute logged batch expectations to their slices: a batch ends at its last slice name
    exp_logged = 0.0; n_logged = 0; exp_model = 0.0; n_model = 0
    i = 0
    while i < len(rows):
        r = rows[i]
        if r["name"] in logged:
            nb, e = logged[r["name"]]
            exp_logged += e; n_logged += nb
            # the nb slices ending here are accounted by the logged value; remove the model estimates already added for them
            back = rows[max(0, i - nb + 1): i + 1]
            for x in back[:-1]:
                exp_model -= x["k"] * x["hit"] * math.exp(-1.0275 * x["E"] + 0.33); n_model -= 1
            i += 1
            continue
        exp_model += r["k"] * r["hit"] * math.exp(-1.0275 * r["E"] + 0.33); n_model += 1
        i += 1
    mem = sum(r["k"] for r in rows)
    fa = [json.loads(l) for l in open(d + "/found.jsonl") if l.strip()] if os.path.exists(d + "/found.jsonl") else []
    fl = [f for f in fa if not f.get("near_miss")]                       # design-Q successes (what "expected" predicts)
    near = [{k: f[k] for k in ("name", "k", "g", "digits")} for f in fa if f.get("near_miss")]   # first-PRP rows above the record
    fams = sorted(set(re.sub(r"_v\d+$|_w\d+$", "", r["name"].split("@")[0]) for r in rows))
    Q = json.load(open(d + "/my_specs.json"))[0]["Q"] if os.path.exists(d + "/my_specs.json") else None
    out.append(dict(dir=d, Q=Q, families=fams[:6], slices=len(rows), members=mem,
                    hit_mass_members=sum(r["k"] * r["hit"] for r in rows),
                    mean_E=sum(r["k"] * r["E"] for r in rows) / max(mem, 1),
                    tests=sum(r["tests"] for r in rows), prps=sum(r["prps"] for r in rows),
                    expected_logged=exp_logged, slices_logged=n_logged, expected_model=max(exp_model, 0.0), slices_model=n_model,
                    found=len(fl), g=[f["g"] for f in fl], hits=[{k: f[k] for k in ("name", "k", "g", "digits")} for f in fl], near_misses=near))
print("[ty]", json.dumps(out))

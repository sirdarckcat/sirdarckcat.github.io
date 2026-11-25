import json, os, re, sys
# campaign3 tally of one or more campaign dirs (the cards' own logs): slices, members, hit mass, mean E^, expected design hits (logged per batch),
# expected near-misses per threshold (logged per batch), found lines; first and last batch time.  Usage: t3.py DIR...  (default: /content/c170r /content/c170g); "since": the same sums over the batches from T3_SINCE on
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) tests=(\d+) prp=(\d+) p\^=(\S+) alive/k=(\S+) E\^=(\S+) hit%=(\S+) found=(\d+)")
bat = re.compile(r"^(\S+) batch \S+ \((\d+) slices\).*expected hits ([\d.e+-]+)")
nr = re.compile(r"expected near>=(\d+) ([\d.e+-]+)")
out = []
DIRS = [a for a in sys.argv[1:] if os.path.isdir(a)] or ["/content/c170r", "/content/c170g"]   # on a card (colab exec -f: argv is the kernel's) the campaign dirs
for d in DIRS:
    if not os.path.exists(os.path.join(d, "gpu3_stats.log")):
        continue
    nb = ns = 0; eh = 0.0; near = {}; first = last = None; T0 = os.environ.get("T3_SINCE", "2026-11-24T19:59:08Z"); s_nb = s_ns = 0; s_eh = 0.0; s_near = {}
    for l in open(os.path.join(d, "gpu3_stats.log")):
        m = bat.match(l)
        if not m:
            continue
        nb += 1; ns += int(m.group(2)); eh += float(m.group(3))
        first = first or m.group(1); last = m.group(1)
        mn = nr.search(l)
        if mn:
            near[mn.group(1)] = near.get(mn.group(1), 0.0) + float(mn.group(2))
        if m.group(1) >= T0:
            s_nb += 1; s_ns += int(m.group(2)); s_eh += float(m.group(3))
            if mn:
                s_near[mn.group(1)] = s_near.get(mn.group(1), 0.0) + float(mn.group(2))
    seen = set(); mem = hm = eE = 0; tests = prps = 0
    if os.path.exists(os.path.join(d, "search.log")):
        for l in open(os.path.join(d, "search.log")):
            m = pat.match(l)
            if m and m.group(1) not in seen:
                seen.add(m.group(1)); k = int(m.group(3)) - int(m.group(2))
                mem += k; hm += k * float(m.group(9)) / 100; eE += k * float(m.group(8)); tests += int(m.group(4)); prps += int(m.group(5))
    fd = [json.loads(l) for l in open(os.path.join(d, "found.jsonl")) if l.strip()] if os.path.exists(os.path.join(d, "found.jsonl")) else []
    out.append(dict(dir=os.path.basename(d.rstrip("/")), batches=nb, slices_batched=ns, slices=len(seen), members=mem, hit_mass=hm, mean_E=eE / max(mem, 1),
                    tests=tests, prps=prps, exp_hits=eh, exp_near=near, since=dict(T0=T0, batches=s_nb, slices=s_ns, exp_hits=s_eh, exp_near=s_near), first=first, last=last,
                    found=[{k: f.get(k) for k in ("name", "k", "g", "digits", "near_miss", "Q")} for f in fd]))
print("[t3]", json.dumps(out))

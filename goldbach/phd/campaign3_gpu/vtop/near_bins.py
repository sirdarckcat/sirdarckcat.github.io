import json, re, datetime, os
def ts(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
B = {}
for l in open("/content/c170v/gpu3_stats.log"):
    t = ts(l.split()[0])
    if t < ts("2026-11-23T17:00:00Z"):
        continue
    m = re.search(r"expected near>=\d+ ([\d.e+-]+)", l); h = re.search(r"expected hits ([\d.e+-]+)", l); c = re.search(r"batch q170000_m89_p\dc(\d+)_", l)
    if m and h:
        k = int((t - ts("2026-11-23T17:00:00Z")) // 300)
        B.setdefault(k, []).append((float(m.group(1)), float(h.group(1)), int(c.group(1)) if c else -1))
print("[bn] 5-min bins from 17:00Z: start chunk | batches | mean near a batch | mean hits a batch")
print("[bn]", " ; ".join(f"{17 + (k * 5) // 60:02d}:{(k * 5) % 60:02d} c{min(x[2] for x in v)} n{len(v)} {sum(x[0] for x in v) / len(v) * 1e6:.3f} {sum(x[1] for x in v) / len(v) * 1e7:.3f}" for k, v in sorted(B.items())))
def stat(f):
    s = json.load(open(f)); tot = below = 0
    for v in s:
        r = v["residual"] if isinstance(v["residual"], list) else json.loads(v["residual"])
        tot += len(r); below += sum(1 for q in r if int(q) < 158209)
    return tot / len(s), below / len(s)
out = []
for c in list(range(186, 200, 2)) + list(range(200, 210, 2)):
    f = f"/content/vec89/vec_{c:06d}.json"
    if os.path.exists(f):
        t, b = stat(f); out.append(f"c{c} {t:.2f}/{b:.1f}")
print("[bn] chunks rows/below-158209:", " ; ".join(out))

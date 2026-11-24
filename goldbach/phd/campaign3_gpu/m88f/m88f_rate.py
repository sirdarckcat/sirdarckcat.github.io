import json, re, time, calendar, os
def ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
pat = re.compile(r"^(\S+Z) batch (\S+) \((\d+) slices\) ([\d.]+)s: tests (\d+) counted.*expected hits (\S+), found (\d+)")
def stats(D, t_lo, t_hi):
    v = []
    for l in open(D + "/gpu3_stats.log"):
        m = pat.match(l)
        if m and t_lo <= ts(m.group(1)) < t_hi:
            v.append((ts(m.group(1)), int(m.group(3)), float(m.group(4)), int(m.group(5)), float(m.group(6))))
    if len(v) < 3:
        return None
    span = v[-1][0] - v[0][0]; nb = len(v) - 1                        # wall time between the first and the last batch end
    sl = sum(x[1] for x in v[1:]); eh = sum(x[4] for x in v[1:])
    return dict(batches=nb, span=span, wall_per_batch=span / nb, slices=sl, members_s=sl * (1 << 25) / span, hits_s=eh / span, tests_s=sum(x[3] for x in v[1:]) / span)
def rows(D):
    s = json.load(open(D + "/my_specs.json")); r = [len(json.loads(x["residual"]) if isinstance(x["residual"], str) else x["residual"]) for x in s]
    al = [float(m.group(1)) for m in (re.search(r"alive/k=([\d.]+)", l) for l in open(D + "/search.log")) if m][-200:]
    return len(s), sum(r) / len(r), min(r), max(r), sum(al) / max(1, len(al))
now = time.time()
o = stats("/content/c170", ts("2026-11-23T16:20:00Z"), ts("2026-11-23T16:50:00Z"))
n = stats("/content/c170f", ts("2026-11-23T16:52:30Z"), now + 60)
ro, rn = rows("/content/c170"), rows("/content/c170f")
print("[mr]", os.popen("hostname").read().strip(), "| old c170 16:20-16:50:", {k: round(v, 4) if isinstance(v, float) else v for k, v in (o or {}).items()})
print("[mr] new c170f 16:52:30-now:", {k: round(v, 4) if isinstance(v, float) else v for k, v in (n or {}).items()})
print(f"[mr] rows: old {ro[0]} vectors, residual mean {ro[1]:.1f} ({ro[2]}-{ro[3]}), alive/k {ro[4]:.1f} | new {rn[0]} vectors, residual mean {rn[1]:.1f} ({rn[2]}-{rn[3]}), alive/k {rn[4]:.1f}")
if o and n:
    print(f"[mr] members/s x{n['members_s'] / o['members_s']:.4f} | expected hits/s x{n['hits_s'] / o['hits_s']:.4f} | hits/s old {o['hits_s']:.4e} new {n['hits_s']:.4e}")

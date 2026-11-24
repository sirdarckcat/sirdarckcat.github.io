# On a card: expected design hits / near-misses a second in fixed windows of its own campaign's gpu3_stats.log (the day-one report).
import calendar, os, re, time
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
run = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
d = re.search(r"--campaign (\S+)", run).group(1)
pat = re.compile(r"^(\S+Z) batch \S+ \((\d+) slices\) ([\d.]+)s: .*?expected hits (\S+?),(?: expected near>=(\d+) (\S+?),)?")
V = [(ts(m.group(1)), int(m.group(2)), float(m.group(4)), float(m.group(6)) if m.group(6) else None) for m in map(pat.match, open(d + "/gpu3_stats.log")) if m]
now = time.time()
W = {"/content/c170r": [("cap 1248-1249", "2026-11-23T20:30:00Z", "2026-11-24T02:40:00Z"), ("cap 1250", "2026-11-24T03:30:00Z", None)],
     "/content/c170g": [("all", "2026-11-23T00:00:00Z", None)]}[d]
out = []
for lab, a, b in W:
    a = ts(a); b = ts(b) if b else now
    v = [x for x in V if a <= x[0] < b]
    if len(v) < 3:
        out.append(f"{lab}: too few"); continue
    span = v[-1][0] - v[0][0]; w = v[1:]; nn = [x[3] for x in w if x[3] is not None]
    out.append(f"{lab} {time.strftime('%H:%M', time.gmtime(v[0][0]))}-{time.strftime('%H:%M', time.gmtime(v[-1][0]))}: {len(w)} batches, {sum(x[1] for x in w) / span:.3f} slices/s, design hits/s {sum(x[2] for x in w) / span:.4e}, near/s {(sum(nn) / span) if nn else 0:.4e}")
print("[rc]", d, "|", " | ".join(out))

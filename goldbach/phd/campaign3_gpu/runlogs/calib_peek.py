# Per-hour calibration lines for the --near-miss 140,000 calibration (the lead, 25 Nov 18:52Z; the consultant's format), from this RTX card's own logs:
# one JSON object an hour: card, hour_start (UTC), T (the --near-miss in force), batches, windows (2^24-member windows sieved), members_scanned, kept_tested (the kept members a window
# times windows), expected_near (sum of the batch lines' "expected near>=T"), expected_design (sum of "expected hits"), found (events written), events [{g, N, name, k}], down_s (gaps
# over 30 s between batch lines, i.e. downtime or a restart), partial (the hour is not wholly covered: drop it from both the expectation and the count).
import calendar, json, os, re, socket, sys, time
START = "2026-11-25T19:55:00Z"
C = "/content/c170r"
pat = re.compile(r"^(\S+) batch .*?\((\d+) slices\) .*?expected hits ([\d.e+-]+), (?:expected near>=(\d+) ([\d.e+-]+), )?found (\d+)")
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
t0 = ts(START)
rows = []
for l in open(C + "/gpu3_stats.log"):
    m = pat.match(l)
    if m and ts(m.group(1)) >= t0:
        rows.append(dict(t=ts(m.group(1)), n=int(m.group(2)), eh=float(m.group(3)), T=int(m.group(4) or 0), en=float(m.group(5) or 0), f=int(m.group(6)),
                         drain="carry-over drain" in l))
ev = []
for fn in ("found.jsonl", "near_events.jsonl"):
    p = os.path.join(C, fn)
    if os.path.exists(p):
        for l in open(p):
            if l.strip():
                r = json.loads(l)
                if r.get("near_miss"):
                    ev.append(r)
# events by the batch that wrote them: the batch lines' found counts in order (found.jsonl and near_events.jsonl merged in N order of writing is not kept, so events are matched to batches
# by count only; the per-hour count is exact, the order within an hour is the files')
seen = set(); evs = []
for r in ev:
    if r["N"] not in seen:
        seen.add(r["N"]); evs.append(r)
# events written before START are excluded by count: the found lines of batches before START
pre = sum(int(m.group(6)) for m in (pat.match(l) for l in open(C + "/gpu3_stats.log")) if m and ts(m.group(1)) < t0)
evs = evs[pre:] if pre <= len(evs) else []
out = {}; k = 0
for i, r in enumerate(rows):
    h = r["t"] // 3600 * 3600
    o = out.setdefault(h, dict(card=socket.gethostname(), hour_start=time.strftime("%Y-%m-%dT%H:00:00Z", time.gmtime(h)), T=r["T"], batches=0, windows=0, expected_near=0.0,
                               expected_design=0.0, found=0, events=[], down_s=0, first=r["t"], last=r["t"]))
    o["batches"] += 0 if r["drain"] else 1; o["windows"] += r["n"]; o["expected_near"] += r["en"]; o["expected_design"] += r["eh"]; o["found"] += r["f"]
    o["T"] = r["T"] or o["T"]; o["last"] = r["t"]
    if i and r["t"] - rows[i - 1]["t"] > 30:
        o["down_s"] += r["t"] - rows[i - 1]["t"]
    for _ in range(r["f"]):
        if k < len(evs):
            e = evs[k]; o["events"].append(dict(g=int(e["g"]), N=e["N"], name=e.get("name"), k=int(e["k"]), sub_record=bool(e.get("sub_record")))); k += 1
for h in sorted(out):
    o = out[h]
    o["members_scanned"] = o["windows"] * (1 << 24); o["kept_tested"] = o["windows"] * 251904
    o["partial"] = bool(o["down_s"] > 0 or o["first"] - h > 60 or h + 3600 - o["last"] > 60)
    del o["first"], o["last"]
    print("[cal]", json.dumps(o))

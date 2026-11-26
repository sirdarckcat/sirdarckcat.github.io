# Per-hour calibration lines for the --near-miss 140,000 calibration (the lead, 25 Nov 18:52Z; the consultant's format), from this RTX card's own logs (v2, 25 Nov 23:10Z).
# One JSON object per hour and near-miss threshold T (an hour in which T changed is split, each piece partial): card, hour_start (UTC), T, batches, windows (2^24-member windows
# sieved), members_scanned, kept_tested (the kept members actually Fermat-tested: per batch, 125,952 a window at keep 0.75% or 251,904 at 1.5%, i.e. 512 selection blocks of
# 2^15 members x ceil(2^15 (1 - f)), the keep in force told by the mean tests a window, < 2.65M at 0.75%, of each run of batch lines between restarts), tests_counted (the batch lines' "tests N counted"), keep_batches,
# expected_near (sum of the batch lines' "expected near>=T"), expected_design (sum of "expected hits"), found (events written), events [{g, N, name, k, sub_record, t, rows}] (rows: the vector's residual rows below T, in [T, g), the row of g, the residual count and the two largest cover moduli, from its spec on the card; each
# matched to the batch line that wrote it by its vector name inside the batch's name range; unmatched counts the batch found counts no event could be matched to), down_s (gaps
# over 30 s between batch lines: downtime), gaps ([time, s] of every gap over 5 s: restarts and pauses, which are below 30 s and so not in down_s), partial (the piece does not
# cover the whole hour: first line more than 60 s after the hour starts, last more than 60 s before it ends, or down_s > 0).
import calendar, json, os, re, socket, sys, time
START = "2026-11-25T19:55:00Z"
C = "/content/c170r"
pat = re.compile(r"^(\S+) batch (\S+)\.\.(\S+) \((\d+) slices\) .*?tests (\d+) counted.*?expected hits ([\d.e+-]+), (?:expected near>=(\d+) ([\d.e+-]+), )?found (\d+)")
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
def key(name):                                       # q170000_m89r491_p0c01147_v866@3382593 -> ("q170000_m89r491_p0c01147", 866)
    m = re.match(r"^(.*)_v(\d+)@\d+$", name or "")
    return (m.group(1), int(m.group(2))) if m else None
def rows_of(name, g, T):
    # the event's vector's residual rows (the uncovered primes q < Q of its spec, i.e. its alive rows) from /content/vec491/vec_<chunk>.json: below T, in [T, g), the row of g
    # (= rows below g), and the vector's residual count; None when the spec file is gone
    try:
        base = name.split("@")[0]; ch = int(re.search(r"c(\d+)_v\d+$", base).group(1))
        for sp in json.load(open("/content/vec491/vec_%06d.json" % ch)):
            if sp.get("name") == base:
                res = sp["residual"]; res = json.loads(res) if isinstance(res, str) else res; res = [int(q) for q in res]
                import bisect
                bT, bg = bisect.bisect_left(res, T), bisect.bisect_left(res, g)
                return dict(below_T=bT, T_to_g=bg - bT, row_of_g=bg, residual=len(res), cover_moduli=sorted(int(c[0]) for c in sp["cover"])[-2:])
    except Exception:
        return None
    return None
t0 = ts(START)
rows = []
for l in open(C + "/gpu3_stats.log"):
    m = pat.match(l)
    if m and ts(m.group(1)) >= t0:
        rows.append(dict(t=ts(m.group(1)), a=key(m.group(2)), b=key(m.group(3)), n=int(m.group(4)), te=int(m.group(5)),
                         eh=float(m.group(6)), T=int(m.group(7) or 0), en=float(m.group(8) or 0), f=int(m.group(9)), drain="carry-over drain" in l))
# the keep in force: it changes only at a restart, so the batch lines are cut into runs at gaps over 5 s and each run is classified by its mean tests a window (single batches
# swing under --carry-over, which moves undecided members between batches)
runs, cur = [], []
for i, r in enumerate(rows):
    if i and r["t"] - rows[i - 1]["t"] > 5:
        runs.append(cur); cur = []
    cur.append(r)
if cur:
    runs.append(cur)
for run in runs:
    keep = "0.0075" if sum(r["te"] for r in run) / max(1, sum(r["n"] for r in run)) < 2.65e6 else "0.015"
    for r in run:
        r["keep"], r["kept"] = keep, r["n"] * (125952 if keep == "0.0075" else 251904)
ev = []; seen = set()
for fn in ("found.jsonl", "near_events.jsonl"):
    p = os.path.join(C, fn)
    if os.path.exists(p):
        for l in open(p):
            if l.strip():
                r = json.loads(l)
                if r.get("near_miss") and r["N"] not in seen:
                    seen.add(r["N"]); ev.append(r)
used = set(); out = {}
for i, r in enumerate(rows):
    h = r["t"] // 3600 * 3600
    o = out.get((h, r["T"]))
    if o is None:
        o = out[(h, r["T"])] = dict(card=socket.gethostname(), hour_start=iso(h)[:14] + "00:00Z", T=r["T"], batches=0, windows=0, members_scanned=0, kept_tested=0,
                                     tests_counted=0, keep_batches={}, expected_near=0.0, expected_design=0.0, found=0, events=[], unmatched=0, down_s=0, gaps=[],
                                     first=r["t"], last=r["t"])
    o["batches"] += 0 if r["drain"] else 1; o["windows"] += r["n"]; o["kept_tested"] += r["kept"]; o["tests_counted"] += r["te"]
    o["keep_batches"][r["keep"]] = o["keep_batches"].get(r["keep"], 0) + 1
    o["expected_near"] += r["en"]; o["expected_design"] += r["eh"]; o["found"] += r["f"]; o["last"] = r["t"]
    if i:
        gap = r["t"] - rows[i - 1]["t"]
        if gap > 5:
            o["gaps"].append([iso(r["t"]), gap])
        if gap > 30:
            o["down_s"] += gap
    need = r["f"]
    for j, e in enumerate(ev):
        if need and j not in used and r["a"] and r["b"] and key(e.get("name")) and r["a"] <= key(e.get("name")) <= r["b"]:
            used.add(j); need -= 1
            o["events"].append(dict(g=int(e["g"]), N=e["N"], name=e.get("name"), k=int(e["k"]), sub_record=bool(e.get("sub_record")), t=iso(r["t"]),
                                    rows=rows_of(e.get("name"), int(e["g"]), r["T"])))
    o["unmatched"] += need
for hk in sorted(out):
    o = out[hk]; h = hk[0]
    o["members_scanned"] = o["windows"] * (1 << 24)
    o["partial"] = bool(o["down_s"] > 0 or o["first"] - h > 60 or h + 3600 - o["last"] > 60)
    del o["first"], o["last"]
    print("[cal]", json.dumps(o))

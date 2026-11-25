import calendar, re, sys, time, json
W = [("control", "2026-11-25T21:08:00Z", "2026-11-25T21:18:00Z"), ("test", "2026-11-25T21:25:00Z", "2026-11-25T22:25:00Z")]
pat = re.compile(r"^(\S+) batch .*?\((\d+) slices\) ([\d.]+)s: tests (\d+) counted, (\d+) computed .*?, (\d+) launches, expected hits ([\d.e+-]+)(?:, expected near>=(\d+) ([\d.e+-]+))?")
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
rows = [m for m in (pat.match(l) for l in open("/content/c170r/gpu3_stats.log")) if m]
for name, a, b in W:
    A, B = ts(a), ts(b)
    sel = [m for m in rows if A <= ts(m.group(1)) < B]
    if len(sel) < 2:
        print("[ab]", name, "too few batches", len(sel)); continue
    span = ts(sel[-1].group(1)) - ts(sel[0].group(1))
    s = sel[1:]
    S = lambda i, f=float: sum(f(m.group(i)) for m in s)
    print("[ab]", json.dumps(dict(window=name, start=a, end=b, batches=len(s), span_s=span, windows_per_s=S(2, int) / span, counted_per_s=S(4, int) / span / 1e6,
                                  computed_per_s=S(5, int) / span / 1e6, launches_per_batch=S(6, int) / len(s), exp_hits_per_s=S(7) / span,
                                  exp_near_per_s=sum(float(m.group(9) or 0) for m in s) / span, T=sorted(set(m.group(8) for m in s)))))

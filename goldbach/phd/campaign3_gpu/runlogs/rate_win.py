# Expected design hits and near-misses a second from gpu3_stats.log lines (their own time stamps) inside [T0, T1): python3 rate_win.py LOG T0 T1  (or '-' for stdin)
import calendar, re, sys, time
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
a, b = ts(sys.argv[2]), ts(sys.argv[3])
pat = re.compile(r"^(\S+Z) batch \S+ \((\d+) slices\) ([\d.]+)s: .*?expected hits (\S+?),(?: expected near>=(\d+) (\S+?),)?")
v = [(ts(m.group(1)), int(m.group(2)), float(m.group(4)), float(m.group(6)) if m.group(6) else None) for m in map(pat.match, src) if m]
v = [x for x in v if a <= x[0] < b]
if len(v) < 3:
    print("too few batches", len(v)); sys.exit()
span = v[-1][0] - v[0][0]; w = v[1:]
h = sum(x[2] for x in w); nn = [x[3] for x in w if x[3] is not None]
print(f"batches {len(w)} | span {span} s | slices a second {sum(x[1] for x in w) / span:.3f} | expected design hits a second {h / span:.4e} | expected near-misses a second {sum(nn) / span:.4e} ({len(nn)} batches logged)" if nn else
      f"batches {len(w)} | span {span} s | slices a second {sum(x[1] for x in w) / span:.3f} | expected design hits a second {h / span:.4e} | near-misses not logged")

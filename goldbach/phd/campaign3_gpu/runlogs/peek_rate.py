import re, time, calendar
pat = re.compile(r"^(\S+) batch \S+ \((\d+) slices\) ([\d.]+)s: tests (\d+) counted, (\d+) computed .*?expected hits ([\d.e+-]+)")
for d in ("/content/c170r", "/content/c170g"):
    try:
        L = open(d + "/gpu3_stats.log").read().splitlines()[-3000:]
    except OSError:
        continue
    rows = []
    for l in L:
        m = pat.match(l)
        if m:
            t = calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"))
            rows.append((t, int(m.group(2)), float(m.group(3)), int(m.group(4)), int(m.group(5)), float(m.group(6))))
    t1 = rows[-1][0]; sel = [r for r in rows if r[0] > t1 - 3600]
    span = sel[-1][0] - sel[0][0]
    n = len(sel) - 1
    sl = sum(r[1] for r in sel[1:]); tc = sum(r[3] for r in sel[1:]); tp = sum(r[4] for r in sel[1:]); eh = sum(r[5] for r in sel[1:]); bt = sum(r[2] for r in sel[1:])
    print(f"[rt] {d} last hour {span} s: {n} batches, {sl} slices, {sl/span:.3f} slices/s, batch wall {span/n:.3f} s (logged mean {bt/n:.3f} s), "
          f"tests counted {tc/sl:.0f} computed {tp/sl:.0f} a slice, {tp/span/1e6:.3f} M tests computed/s, expected hits/s {eh/span:.4e}")

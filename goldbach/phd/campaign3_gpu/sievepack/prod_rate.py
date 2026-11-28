# Production A/B of the deep head: per card, the batches logged in /content/c170v/gpu3_stats.log from T0 on: batch time (span / intervals), expected
# near-misses >= 157,837 and design hits a batch and a second, tests a batch, slices a batch. T0 = 12:08:00Z (after the 12:06Z restarts and the head's tables).
import datetime, re, sys
T0 = datetime.datetime(2026, 11, 23, 13, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
T1 = 1e18
R = []
for l in open("/content/c170v/gpu3_stats.log"):
    ts = datetime.datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    if ts < T0 or ts > T1:
        continue
    R.append((ts, float(re.search(r"expected near>=\d+ ([\d.e+-]+)", l).group(1)), float(re.search(r"expected hits ([\d.e+-]+)", l).group(1)),
              int(re.search(r"tests (\d+) counted", l).group(1)), int(re.search(r"\((\d+) slices\)", l).group(1))))
n = len(R); span = R[-1][0] - R[0][0] if n > 1 else float("nan")
near = sum(r[1] for r in R[1:]); hits = sum(r[2] for r in R[1:])
print(f"[ab] batches {n} | span {span:.0f} s | batch {span / (n - 1):.4f} s | near/batch {near / (n - 1):.4e} | near/s {near / span:.4e} | hits/s {hits / span:.4e} | "
      f"tests/batch {sum(r[3] for r in R[1:]) / (n - 1):.0f} | slices/batch {sum(r[4] for r in R[1:]) / (n - 1):.3f} | first {datetime.datetime.utcfromtimestamp(R[0][0]):%H:%M:%S} last {datetime.datetime.utcfromtimestamp(R[-1][0]):%H:%M:%S}")

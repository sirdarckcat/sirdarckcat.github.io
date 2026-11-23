# RTX production in three windows of /content/c170v/gpu3_stats.log: W0 bottom placement (16:50-17:28:30Z), W1 top placement (17:30:30-18:04:30Z), W2 top + one-pass (18:12:30Z on):
# batch time (span / intervals), expected near-misses >= 158,209 and design hits a second, tests a batch.
import datetime, re
def ts(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
W = {"W0 bottom": ("2026-11-23T16:50:00Z", "2026-11-23T17:28:30Z"), "W1 top": ("2026-11-23T17:30:30Z", "2026-11-23T18:04:30Z"), "W2 top+onepass": ("2026-11-23T18:12:30Z", "2026-11-23T23:59:00Z")}
L = open("/content/c170v/gpu3_stats.log").read().splitlines()
out = {}
for k, (a, b) in W.items():
    R = []
    for l in L:
        t = ts(l.split()[0])
        if ts(a) <= t < ts(b):
            m1, m2, m3 = re.search(r"expected near>=\d+ ([\d.e+-]+)", l), re.search(r"expected hits ([\d.e+-]+)", l), re.search(r"tests (\d+) counted", l)
            if m1 and m2 and m3:
                R.append((t, float(m1.group(1)), float(m2.group(1)), int(m3.group(1))))
    if len(R) < 3:
        print("[p3]", k, "too few batches", len(R)); continue
    span = R[-1][0] - R[0][0]; n = len(R) - 1
    out[k] = dict(batch=span / n, near_s=sum(r[1] for r in R[1:]) / span, hits_s=sum(r[2] for r in R[1:]) / span, near_b=sum(r[1] for r in R[1:]) / n, tests_b=sum(r[3] for r in R[1:]) / n)
    print(f"[p3] {k:15s} batches {n:5d} | batch {out[k]['batch']:.4f} s | near/batch {out[k]['near_b']:.4e} | near/s {out[k]['near_s']:.4e} | hits/s {out[k]['hits_s']:.4e} | tests/batch {out[k]['tests_b']:.0f}")
ks = list(out)
for a, b in zip(ks, ks[1:]):
    print(f"[p3] {b} / {a}: batch x{out[b]['batch'] / out[a]['batch']:.4f} | near a batch x{out[b]['near_b'] / out[a]['near_b']:.4f} | near/s x{out[b]['near_s'] / out[a]['near_s']:.4f} | hits/s x{out[b]['hits_s'] / out[a]['hits_s']:.4f}")

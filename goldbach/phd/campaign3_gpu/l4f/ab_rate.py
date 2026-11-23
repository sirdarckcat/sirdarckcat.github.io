# The L4 keep-fraction A/B: expected design hits a second and members a second of this card's campaign (c170f) in a window before the switch [PRE0, T0) and one after
# [T0 + 120 s, T1) (the same clock windows on every L4; the stats lines' own timestamps). PRE0 / T0 / T1 are set by the launcher (sed).
import calendar, os, re, time
PRE0, T0, T1 = "2026-11-23T16:53:00Z", "2026-11-23T17:35:00Z", "2026-11-23T18:35:00Z"
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
pat = re.compile(r"^(\S+Z) batch \S+ \((\d+) slices\) ([\d.]+)s: tests (\d+) counted.*expected hits (\S+), found (\d+)")
def win(a, b):
    v = [(ts(m.group(1)), int(m.group(2)), int(m.group(4)), float(m.group(5))) for m in map(pat.match, open("/content/c170f/gpu3_stats.log")) if m and a <= ts(m.group(1)) < b]
    if len(v) < 3:
        return None
    span = v[-1][0] - v[0][0]
    return dict(n=len(v) - 1, span=span, members_s=sum(x[1] for x in v[1:]) * (1 << 25) / span, hits_s=sum(x[3] for x in v[1:]) / span, tests_s=sum(x[2] for x in v[1:]) / span,
                hits_per_slice=sum(x[3] for x in v[1:]) / sum(x[1] for x in v[1:]))
pre, post = win(ts(PRE0), ts(T0)), win(ts(T0) + 120, ts(T1))
env = [e for e in open("/content/next_campaign_env").read().split() if e.startswith("SKIPF=")]
print("[ab]", os.popen("hostname").read().strip(), env, "| pre", {k: (f"{v:.4e}" if isinstance(v, float) else v) for k, v in (pre or {}).items()})
print("[ab] post", {k: (f"{v:.4e}" if isinstance(v, float) else v) for k, v in (post or {}).items()})
if pre and post:
    print(f"[ab] post/pre: hits/s x{post['hits_s'] / pre['hits_s']:.4f} | members/s x{post['members_s'] / pre['members_s']:.4f} | hits a slice x{post['hits_per_slice'] / pre['hits_per_slice']:.4f}")

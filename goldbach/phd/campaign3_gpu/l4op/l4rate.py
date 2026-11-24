# The L4/T4 deploy (sieve options + one-pass + top-16 levels): this card's campaign (c170f) before [PRE0, PRE1) and after [POST0, now): batch time, members a second,
# expected design hits a second and a slice (stats lines' own timestamps). PRE0/PRE1/POST0 set by the launcher (sed).
import calendar, os, re, time
PRE0, PRE1, POST0 = "2026-11-23T18:35:30Z", "2026-11-23T18:54:30Z", "2026-11-23T18:57:00Z"
ts = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
pat = re.compile(r"^(\S+Z) batch \S+ \((\d+) slices\) ([\d.]+)s: tests (\d+) counted.*expected hits (\S+), found (\d+)")
def win(a, b):
    v = [(ts(m.group(1)), int(m.group(2)), float(m.group(5))) for m in map(pat.match, open("/content/c170f/gpu3_stats.log")) if m and a <= ts(m.group(1)) < b]
    if len(v) < 3:
        return None
    span = v[-1][0] - v[0][0]; n = len(v) - 1; sl = sum(x[1] for x in v[1:])
    return dict(n=n, batch=span / n, members_s=sl * (1 << 25) / span, hits_s=sum(x[2] for x in v[1:]) / span, hits_slice=sum(x[2] for x in v[1:]) / sl)
pre, post = win(ts(PRE0), ts(PRE1)), win(ts(POST0), time.time() + 60)
env = [e for e in open("/content/next_campaign_env").read().split() if e.startswith(("KLO=", "SKIPF=", "DEEP_GEN_ONEPASS"))]
f = lambda d: {k: (f"{v:.4e}" if isinstance(v, float) else v) for k, v in (d or {}).items()}
print("[lr]", os.popen("hostname").read().strip(), env, "| pre", f(pre), "| post", f(post))
if pre and post:
    print(f"[lr] post/pre: batch x{post['batch'] / pre['batch']:.4f} | members/s x{post['members_s'] / pre['members_s']:.4f} | hits/s x{post['hits_s'] / pre['hits_s']:.4f} | hits a slice x{post['hits_slice'] / pre['hits_slice']:.4f}")

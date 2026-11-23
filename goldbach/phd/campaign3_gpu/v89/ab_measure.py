# The lead's gate: expected first-PRP rows >= the record (design hits included) per second, from the batch stats of the 88-moduli phase
# (/content/c170 since T88) and of the 89-moduli phase (/content/c170v), batches 2..n of each phase (the first carries the start-up).
import re, sys, datetime
def parse(t): return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
pat = re.compile(r"^(\S+Z) batch .*\((\d+) slices\) ([\d.]+)s: .*expected hits ([\d.e+-]+), expected near>=(\d+) ([\d.e+-]+), found (\d+)")
def phase(f, t_from, t_to=None):
    rec = []
    for l in open(f).read().splitlines():
        m = pat.match(l)
        if m:
            t = parse(m.group(1))
            if t >= t_from and (t_to is None or t <= t_to):
                rec.append((t, int(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(6)), int(m.group(7))))
    if len(rec) < 3:
        return None
    dt = (rec[-1][0] - rec[0][0]).total_seconds()
    eh = sum(r[3] for r in rec[1:]); en = sum(r[4] for r in rec[1:])
    return dict(batches=len(rec), span_s=dt, slices=sum(r[1] for r in rec), batch_s=dt / (len(rec) - 1), hits_per_s=eh / dt, near_per_s=en / dt,
                found=sum(r[5] for r in rec), first=rec[0][0].strftime("%H:%M:%S"), last=rec[-1][0].strftime("%H:%M:%S"))
t88, t89 = parse(sys.argv[1]), parse(sys.argv[2])
a = phase("/content/c170/gpu3_stats.log", t88, t89)
b = phase("/content/c170v/gpu3_stats.log", t89)
for name, x in (("88 moduli (c170)", a), ("89 moduli (c170v)", b)):
    print(f"[ab] {name}: " + (", ".join(f"{k} {v:.4e}" if isinstance(v, float) and v < 1e-2 else f"{k} {v:.3f}" if isinstance(v, float) else f"{k} {v}" for k, v in x.items()) if x else "not enough batches"))
if a and b:
    print(f"[ab] ratio 89 / 88: expected near>=record per second x{b['near_per_s'] / a['near_per_s']:.3f}, expected design hits per second x{b['hits_per_s'] / a['hits_per_s']:.3f}, "
          f"time a member x{(b['batch_s'] / (b['slices'] / b['batches'] * 2**24)) / (a['batch_s'] / (a['slices'] / a['batches'] * 2**25)):.3f}")

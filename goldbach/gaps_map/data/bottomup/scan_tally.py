# Tally of the idle-core CPU scan (uarch session's pipeline, sieve200/search_c.py; /home/user/scan479): found against expected per target, and the exact overshoot of every find from its N alone.
#   python3 scan_tally.py /home/user/scan479 [R]
# Log line: [cover] k=[0,K) Ns (k/s) tests=.. prp=.. p^=.. alive/k=.. E^=.. hit%=.. found=n ; expected successes of a cover = K * hit%/100 * exp(-E^) (the pipeline's own accounting).
# Overshoot of a find at target Q with first prime row g: u = number of primes q in [Q, g) with N - q coprime to all odd primes <= R; geometric under the model, P(u >= m) = (1 - pi)^m, pi = 2 prod r/(r-1)/ln N.
import re, sys, json, math, glob, os
import numpy as np
d = sys.argv[1] if len(sys.argv) > 1 else '/home/user/scan479'
R = int(sys.argv[2]) if len(sys.argv) > 2 else 463
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
P = [int(p) for p in primes_upto(300000) if p > 2]
rs = [p for p in P if p <= R]; c = 2 * math.prod(r / (r - 1) for r in rs)
pat = re.compile(r'^\[(\S+)\] k=\[(\d+),(\d+)\) (\d+)s .*alive/k=([\d.]+) E\^=([\d.]+) hit%=([\d.]+) found=(\d+)')
for tag, Q in (('f479_w', 160367), ('f479t80000_w', 80000), ('f479t90000_w', 90000), ('f479t100000_w', 100000), ('f479lo_w', 120000)):
    logs = sorted(glob.glob(os.path.join(d, tag + '[0-9].log')))
    covers = exp = found = secs = 0
    for f in logs:
        for l in open(f):
            m = pat.match(l)
            if not m: continue
            covers += 1; K = int(m.group(3)) - int(m.group(2)); secs += int(m.group(4)); exp += K * float(m.group(7)) / 100 * math.exp(-float(m.group(6))); found += int(m.group(8))
    if covers == 0: continue
    ev = []
    for f in sorted(glob.glob(os.path.join(d, tag.replace('_w', '_found_w') + '[0-9]*.jsonl'))):
        ev += [json.loads(l) for l in open(f) if l.strip()]
    line = '%-22s target %7d: %5d covers (%.1f core-hours), expected %.4f, found %d (jsonl %d)' % (tag, Q, covers, secs / 3600, exp, found, len(ev))
    if exp > 0 and found > 0: line += ', ln(found/expected) = %+.2f +- %.2f' % (math.log(found / exp), 1 / math.sqrt(found))
    print(line)
    if ev:
        us = []; pis = []
        for e in ev:
            N = int(e['N']); g = int(e['g']); qs = [q for q in P if Q <= q < g]
            u = sum(1 for q in qs if all((N - q) % r != 0 for r in rs)); us.append(u); pis.append(c / math.log(N))
        us = np.array(us); pis = np.array(pis); mean = ((1 - pis) / pis); var = (1 - pis) / pis ** 2; v = (1 - pis) ** us * (1 - pis / 2)
        print('    overshoot of the %d finds (R = %d): rows survived %d against %.1f expected, ratio %.2f +- %.2f, mid-PIT mean %.3f (se %.3f); g from %d to %d' %
              (len(us), R, us.sum(), mean.sum(), us.sum() / mean.sum(), math.sqrt(var.sum()) / mean.sum(), v.mean(), 0.2887 / math.sqrt(len(us)), min(int(e['g']) for e in ev), max(int(e['g']) for e in ev)))

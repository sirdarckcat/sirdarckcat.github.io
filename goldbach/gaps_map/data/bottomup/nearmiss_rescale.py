# Time rescaling of the fleet's own near-miss log: found against expected at the threshold T in force, and the overshoot law beyond T, from the events' N alone.
#   python3 -I nearmiss_rescale.py calib.jsonl [more.jsonl ...] [--R 463]
# Input: the per-hour "[cal]" lines of the GPU session (goldbach/phd/campaign3_gpu/runlogs/calib_peek.py and collect.sh: one JSON object an hour per card, a header object first):
#   card, hour_start, T, batches, windows, members_scanned, kept_tested, expected_near, expected_design, found, events [{g, N, name, k, sub_record}], down_s, partial.
# Hours with partial = true (downtime, restart, or not wholly covered) are dropped from the expectation AND from the count (an event is counted only in a kept hour).
# Output per T: sum of expected_near, events with g >= T, ln(found/expected) +- 1/sqrt(found) with the exact Poisson tail, the dispersion over the hours, the exponent -ln(expected/members),
#   the overshoot of every event beyond T (alive rows u = primes q in [T, g) with N - q coprime to the odd primes <= R, geometric with P(u >= m) = (1 - pi)^m, pi = 2 prod r/(r-1)/ln N),
#   and the survival test at the thresholds above T: events with g >= T' against sum over events of (1 - pi)^(alive rows in [T, T')).
import sys, json, math
import numpy as np
args = [a for a in sys.argv[1:] if not a.startswith('--')]
R = 463
if '--R' in sys.argv: R = int(sys.argv[sys.argv.index('--R') + 1]); args = [a for a in args if a != str(R)]
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
P = primes_upto(400000); rs = [int(p) for p in P if 2 < p <= R]; c = 2 * math.prod(r / (r - 1) for r in rs)
def alive_rows(N, lo, hi):
    q = P[(P >= lo) & (P < hi)]
    if len(q) == 0: return 0
    bad = np.zeros(len(q), bool)
    for r in rs: bad |= (q % r == N % r)
    return int((~bad).sum())
def pois_sf(k, mu):   # P(X >= k) for X ~ Poisson(mu)
    if k <= 0: return 1.0
    s = 0.0; t = math.exp(-mu)
    for i in range(k): s += t; t *= mu / (i + 1)
    return max(0.0, 1.0 - s)
rows = []
for f in args:
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            if o.get('header'): continue
            rows.append(o)
print('%d hour-lines read, %d partial dropped' % (len(rows), sum(1 for o in rows if o.get('partial'))))
by = {}
for o in rows:
    if o.get('partial') or not o.get('T'): continue
    by.setdefault(int(o['T']), []).append(o)
for T in sorted(by):
    hs = by[T]; exp = sum(o['expected_near'] for o in hs); mem = sum(o['members_scanned'] for o in hs)
    ev = [e for o in hs for e in o['events'] if int(e['g']) >= T]
    n = len(ev); dsn = sum(o['expected_design'] for o in hs)
    print('\nT = %d: %d hours (%s cards), %.3g members scanned, expected_near %.3f, expected_design %.4f, events with g >= T: %d' % (T, len(hs), len({o['card'] for o in hs}), mem, exp, dsn, n))
    if exp > 0: print('    exponent -ln(expected_near/members) = %.2f nats' % (-math.log(exp / mem)))
    if n > 0 and exp > 0:
        print('    ln(found/expected) = %+.2f +- %.2f nats; Poisson P(X >= found) = %.3f, P(X <= found) = %.3f' % (math.log(n / exp), 1 / math.sqrt(n), pois_sf(n, exp), 1 - pois_sf(n + 1, exp)))
    elif exp > 0: print('    found 0 against %.3f expected: ln ratio below %+.2f at 1 sd (a lower bound is not defined), P(X = 0) = %.3f' % (exp, -math.log(exp) - 1, math.exp(-exp)))
    hf = np.array([sum(1 for e in o['events'] if int(e['g']) >= T) for o in hs], float); he = np.array([o['expected_near'] for o in hs], float)
    m = he > 0
    if m.sum() > 1: print('    dispersion over the hours: sum (f - e)^2 / e = %.1f on %d hours (expected %d +- %.1f)' % ((((hf - he) ** 2)[m] / he[m]).sum(), m.sum(), m.sum(), math.sqrt(2 * m.sum())))
    if n:
        us = []; pis = []; names = []
        for e in ev:
            N = int(e['N']); g = int(e['g']); us.append(alive_rows(N, T, g)); pis.append(c / math.log(N))
        us = np.array(us); pis = np.array(pis); mean = (1 - pis) / pis; var = (1 - pis) / pis ** 2; v = (1 - pis) ** us * (1 - pis / 2)
        print('    overshoot of the %d events beyond T (R = %d): alive rows survived %d against %.1f expected, ratio %.2f +- %.2f, mid-PIT mean %.3f (se %.3f); g from %d to %d' %
              (n, R, us.sum(), mean.sum(), us.sum() / mean.sum(), math.sqrt(var.sum()) / mean.sum(), v.mean(), 0.2887 / math.sqrt(n), min(int(e['g']) for e in ev), max(int(e['g']) for e in ev)))
        for Tp in (T + 5000, T + 10000, T + 15000, T + 20000, T + 30000):
            if Tp <= max(int(e['g']) for e in ev) + 30000:
                obs = sum(1 for e in ev if int(e['g']) >= Tp)
                ex = sum((1 - pi) ** alive_rows(int(e['N']), T, Tp) for e, pi in zip(ev, pis))
                print('    events with g >= %d: %d against %.1f expected (theta = 1)%s' % (Tp, obs, ex, ('; ln ratio %+.2f +- %.2f' % (math.log(obs / ex), 1 / math.sqrt(obs))) if obs and ex else ''))

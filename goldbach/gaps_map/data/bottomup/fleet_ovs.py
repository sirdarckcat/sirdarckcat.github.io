# Exact overshoot of the fleet's 11 events from N alone (hits.jsonl of the GPU campaign, branch ccr-8ffe9d7a-4ni11u): for a hit at level L (the design Q, or the near-miss threshold) with
# first prime row g, u = number of rows q in [L, g) (primes) with N - q coprime to all odd primes <= R; under the model P(u >= m) = (1 - pi)^m, pi = 2 prod r/(r-1)/ln N.
import json, math, numpy as np
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
P = [int(p) for p in primes_upto(300000) if p > 2]
ev = [json.loads(l) for l in open('fleet_hits.jsonl') if l.strip()]
import re
def level(e):
    if e.get('near_miss'): return e['threshold']
    m = re.search(r'q(\d+)k', e['name']) or re.search(r'q(\d+)', e['name'])
    q = int(m.group(1)); return q * 1000 if q < 1000 else q
for R in (97, 463, 491):
    rs = [p for p in P if p <= R]; c = 2 * math.prod(r / (r - 1) for r in rs)
    rows_out = []; us = []; exps = []; vs = []
    for e in ev:
        N = int(e['N']); g = e['g']; L = level(e)
        qs = [q for q in P if L <= q < g]
        u = sum(1 for q in qs if all((N - q) % r != 0 for r in rs))
        # the row g itself must be alive and prime (first PRP): check it is coprime to the small primes
        pi = c / math.log(N); us.append(u); exps.append((1 - pi) / pi); vs.append((1 - pi) ** u * (1 - pi / 2)); rows_out.append((e['name'][:34], L, g, u, round((1 - pi) / pi, 1)))
    var = sum((1 - (c / math.log(int(e['N'])))) / (c / math.log(int(e['N']))) ** 2 for e in ev)
    print('R = %d (pi about %.4f): %d events, overshoot rows observed %d, model %.1f, ratio %.2f +- %.2f; mid-PIT mean %.3f (0.5, se %.3f)' % (R, c / math.log(int(ev[0]['N'])), len(ev), sum(us), sum(exps), sum(us) / sum(exps), math.sqrt(var) / sum(exps), np.mean(vs), 0.2887 / math.sqrt(len(ev))))
    if R == 463:
        for r in rows_out: print('    %-34s level %6d g %6d alive rows survived %3d (model mean %s)' % r)

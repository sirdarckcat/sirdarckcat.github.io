"""WP9 scorer — single-schema evaluation for external search loops
(AlphaEvolve generative tier).

Usage:
  python3 scorer.py '<schema-json>'
  echo '<schema-json>' | python3 scorer.py

Schema JSON: {"family": <name>, "params": {...}}
Families and params (the L grammar, wp9_closure_theorem.md §4):
  Congruence      {"d": int>=2, "a": int}
  PolyImage       {"k": 2..4, "a": int>=1, "c": int>=1}     # N = a*m^k - c
  ExpFamily       {"a": 2..7, "j": int>=1, "c": int}        # N = j*a^n + c
  MultiPolyBin    {"A": [a,b,c]}                            # binary quadratic
  MultiPolyQuart  {"A": [a,b,c], "B": [a,b,c]}              # product of two
  Cyclotomic      {"n": 3..500}
  Compose         {"parts": [<schema>, <schema>]}           # depth <= 2

Output: one JSON row {family, params, killable, residual_kills,
design_cost, nats_per_residual_kill, verdict, fitness, reason}.

Fitness contract (anti-reward-hack by construction):
  * fitness is computed ONLY from quantities this scorer re-derives from
    primitives (deterministic sieve of Q-range primality, the committed
    c1 residual set, symbolic factorization); nothing the proposer
    asserts is trusted;
  * out-of-grammar or erroring schemas score 0.0;
  * fitness = min(1, killable/CEIL) * min(1, BENCH/nats_per_res_kill),
    so 1.0 requires clearing BOTH filter conditions — any fitness
    >= 0.25 is logged for review and any PASS (== 1.0 thresholds met)
    must be hand-audited before it is treated as real (harness.md).
"""
import json
import math
import os
import sys

import numpy as np
import sympy
from sympy import n_order, primerange

HERE = os.path.dirname(os.path.abspath(__file__))
PHD = os.path.dirname(os.path.dirname(HERE))
Q = 122000
LNB = 200 * math.log(10)
# The two filter constants. BENCH is covering's MARGINAL endgame cost
# (tier-0 T1 measured 0.87-1.31 nats/offset over the last six moduli); it
# tests "is this mechanism worth adding at the margin?". CEIL = 3*sqrt(Q)
# tests "is it a BULK mechanism?" -- deliberately just above the sqrt(Q)
# value-set ceiling that caps every degree>=2 identity family (sec 13c).
# Because row() also enforces the design-entropy budget, clearing CEIL
# implicitly demands cost < lnB/CEIL = 0.44 nats/offset, and the honest
# reference point for a bulk mechanism is covering's AVERAGE, 437 nats /
# 10,607 offsets = 0.041 nats/offset (sec 12). These constants are the
# authoritative definition; the memo quotes them.
BENCH = 1.01
CEIL = 3 * math.sqrt(Q)

_isp = None
_residual = None


def setup():
    global _isp, _residual
    lim = Q + 20000
    s = np.ones(lim, dtype=bool)
    s[:2] = False
    for p in range(2, int(lim ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = False
    _isp = s
    spec = json.load(open(os.path.join(PHD, 'campaign3/base_spec.json')))
    _residual = set(int(q) for q in spec['residual'])


def row(family, params, killable, res, cost, reason, baseline=False):
    """Score a schema.  The design-entropy BUDGET is enforced here: a family
    whose total certificate cost exceeds ln B cannot be bought outright, only
    the affordable fraction of it, so the certified-offset count is scaled by
    lnB/cost.  Without this a per-offset mechanism could advertise thousands
    of certifiable offsets while charging more nats each than the whole
    construction has to spend (the hole the generative tier found on
    2026-07-29: ExpFamily claiming 10,416 offsets at 2.2 nats = 22,900 nats
    against a 460-nat budget)."""
    nprk = cost / res if res else float('inf')
    afford = 1.0 if cost <= LNB else LNB / cost
    eff_killable = killable * afford
    eff_res = res * afford
    if baseline:
        verdict, fitness = 'BASELINE', 0.0
    else:
        verdict = 'PASS' if (eff_killable > CEIL and nprk < BENCH) else 'REJECT'
        fitness = min(1.0, eff_killable / CEIL) * \
            (min(1.0, BENCH / nprk) if res else 0.0)
    if afford < 1.0:
        reason += (" | BUDGET-CAPPED: total cost %.0f nats > lnB %.0f, so at "
                   "most %.0f of %.0f offsets are affordable"
                   % (cost, LNB, eff_killable, killable))
    return dict(family=family, params=params, killable=int(eff_killable),
                claimed_killable=int(killable),
                residual_kills=int(eff_res), design_cost=round(cost, 2),
                nats_per_residual_kill=None if not res else round(nprk, 3),
                verdict=verdict, fitness=round(float(fitness), 4),
                reason=reason)


def ev_congruence(p):
    d, a = int(p['d']), int(p['a'])
    if d < 2:
        raise ValueError('d<2')
    return row('Congruence', p, 0, 0, math.log(d),
               'congruence classes ARE the covering baseline; the escape '
               'filter does not apply', baseline=True)


def ev_polyimage(p):
    k, a, c = int(p['k']), int(p.get('a', 1)), int(p['c'])
    if not (2 <= k <= 4 and a >= 1 and c >= 1):
        raise ValueError('out of grammar')
    kill = res = 0
    d = 2
    while a * d ** k - c < Q:
        v = a * d ** k - c
        if v > 2 and _isp[v]:
            kill += 1
            res += v in _residual
        d += 1
    return row('PolyImage', p, kill, res, (1 - 1 / k) * LNB,
               f'value set <= (Q/a)^(1/{k}); family cost (1-1/{k})lnB')


def ev_expfamily(p):
    a, j, c = int(p['a']), int(p['j']), int(p['c'])
    if not (2 <= a <= 7 and j >= 1):
        raise ValueError('out of grammar')
    svals = [s for s in primerange(500, 3000)][:40]
    qs = [q for q in range(max(3, c + 2), Q, 9973) if _isp[q]][:25]
    costs = []
    for q in qs:
        best = None
        for s in svals:
            if (q - c) % s == 0 or a % s == 0 or j % s == 0:
                continue
            t = (q - c) * pow(j, -1, s) % s
            o = n_order(a, s)
            if pow(t, o, s) == 1:
                lo = math.log(o)
                best = lo if best is None else min(best, lo)
        if best is not None:
            costs.append(best)
    if not costs:
        return row('ExpFamily', p, 0, 0, 0.0, 'no certifying s in sample')
    frac = len(costs) / len(qs)
    mean_c = sum(costs) / len(costs)
    k_est = frac * Q / math.log(Q)          # offsets this family can certify
    # Each order-condition certifies ONE offset and costs ln(ord) nats, so the
    # design must pay mean_c for EVERY offset it claims -- charging only the
    # 867 residuals understated the bill by 12x and let a per-offset mechanism
    # advertise bulk coverage it cannot afford (audit, 2026-07-29).
    return row('ExpFamily', p, k_est, k_est, mean_c * k_est,
               f'per-offset cost ~ln(ord)={mean_c:.2f} charged per certified '
               f'offset (wp7-P3: one offset per order-condition); '
               f'residual-only kills would be {frac * len(_residual):.0f}')


def ev_multipoly_bin(p):
    a, b, c = [int(t) for t in p['A']]
    if a <= 0:
        raise ValueError('need positive leading coeff')
    disc = b * b - 4 * a * c
    red = disc >= 0 and sympy.sqrt(disc).is_integer
    if red:
        return row('MultiPolyBin', p, 0, 0, 0.0,
                   'reducible: linear factors, divisor O(range) -> '
                   'sieve-equivalent')
    return row('MultiPolyBin', p, 0, 0, 0.0,
               'irreducible: representation != compositeness')


def ev_multipoly_quart(p):
    A = [int(t) for t in p['A']]
    B = [int(t) for t in p['B']]
    for f in (A, B):
        if f[0] <= 0 or f[1] * f[1] - 4 * f[0] * f[2] >= 0:
            raise ValueError('factors must be positive definite')
    wph = {}
    for X in (10 ** 6, 10 ** 8):
        W = 10 ** 4
        T = int(X ** 0.25 * 2)
        hits = 0
        for u in range(T):
            for v in range(T):
                va = A[0] * u * u + A[1] * u * v + A[2] * v * v
                if va <= 1:
                    continue
                vb = B[0] * u * u + B[1] * u * v + B[2] * v * v
                if vb > 1 and X <= va * vb < X + W:
                    hits += 1
        wph[X] = (T * T / hits) if hits else float('inf')
    xs = [X for X in wph if wph[X] != float('inf')]
    if len(xs) >= 2:
        lo, hi = min(xs), max(xs)
        th = (math.log(wph[hi]) - math.log(wph[lo])) / (math.log(hi) - math.log(lo))
        reason = (f'enumeration work/offset ~ height^{th:.2f}; at B=10^200 '
                  f'~10^{200 * th:.0f} ops/offset (balanced-representation wall)')
    else:
        reason = 'enumerable sliver already empty at measured heights'
    return row('MultiPolyQuart', p, 0, 0, float('inf'), reason)


def ev_cyclotomic(p):
    n = int(p['n'])
    if not 3 <= n <= 500:
        raise ValueError('out of grammar')
    phi = int(sympy.totient(n))
    count = max(0, int(Q ** (1 / phi)) - 1)
    return row('Cyclotomic', p, count, count * 0.076,
               (1 - 1 / phi) * LNB,
               f'univariate identity family of degree phi({n})={phi}')


def ev_compose(p):
    parts = p['parts']
    if len(parts) != 2:
        raise ValueError('compose arity 2')
    r1 = evaluate(parts[0])
    r2 = evaluate(parts[1])
    if 'Congruence' in (r1['family'], r2['family']):
        return row('Compose', p, r1['killable'] + r2['killable'], 0,
                   r1['design_cost'] + r2['design_cost'],
                   'contains covering baseline; kills additive '
                   '(wp9 §8: no super-additivity found in 60-sample audit)',
                   baseline=True)
    return row('Compose', p, r1['killable'] + r2['killable'],
               r1['residual_kills'] + r2['residual_kills'],
               r1['design_cost'] + r2['design_cost'],
               f'additive composition of [{r1["reason"][:40]}] and '
               f'[{r2["reason"][:40]}]')


EV = dict(Congruence=ev_congruence, PolyImage=ev_polyimage,
          ExpFamily=ev_expfamily, MultiPolyBin=ev_multipoly_bin,
          MultiPolyQuart=ev_multipoly_quart, Cyclotomic=ev_cyclotomic,
          Compose=ev_compose)


def evaluate(schema):
    fam = schema.get('family')
    if fam not in EV:
        return dict(family=str(fam), params=schema.get('params'),
                    killable=0, residual_kills=0, design_cost=0.0,
                    nats_per_residual_kill=None, verdict='REJECT',
                    fitness=0.0, reason='out of grammar')
    try:
        return EV[fam](schema.get('params', {}))
    except Exception as e:
        return dict(family=fam, params=schema.get('params'), killable=0,
                    residual_kills=0, design_cost=0.0,
                    nats_per_residual_kill=None, verdict='REJECT',
                    fitness=0.0, reason=f'evaluator error: {e}')


if __name__ == '__main__':
    setup()
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(evaluate(json.loads(raw)), default=str))

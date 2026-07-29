"""WP9 engine, exhaustive tier: sweep the full schema language L.

Every schema instance compiles to a row:
  (family, params, killable, residual_kills, design_cost_nats,
   nats_per_residual_kill, verdict, reason)
against the LIVE context: c1 cover at Q=122,000 (residual set from
base_spec), B = 10^200, endgame benchmark from tier-0 (1.0 nats/offset).

Filter (wp9 sec 5): a PASS must (1) certify > CEIL = c1*sqrt(Q) distinct
prime offsets AND (2) cost < BENCH nats per residual kill.  Anything
within 4x of BENCH on (2) or 0.5x of CEIL on (1) is logged as a
near-miss for hand review.  Expected result: zero passes.
"""
import itertools
import json
import math
import os
import time

import numpy as np
import sympy
from sympy import primerange, n_order, factorint

HERE = os.path.dirname(os.path.abspath(__file__))
PHD = os.path.dirname(os.path.dirname(HERE))
Q = 122000
LNB = 200 * math.log(10)
BENCH = 1.01          # tier-0 measured covering endgame (nats/offset)
CEIL = 3 * math.sqrt(Q)   # ~1050: univariate value-set ceiling with slack

rows = []


def prime_bitset(limit):
    s = np.ones(limit, dtype=bool)
    s[:2] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = False
    return s


ISP = prime_bitset(Q + 20000)

spec = json.load(open(os.path.join(PHD, 'campaign3/base_spec.json')))
COVER = {int(r): int(a) for r, a in spec['cover']}
RESIDUAL = set(int(q) for q in spec['residual'])


def emit(family, params, killable, res_kills, cost, reason,
         baseline=False, force_pass=None):
    """baseline=True: the schema IS covering (or contains it) — the
    escape filter does not apply; verdict records internal economics.
    force_pass: override for families with their own pass criterion
    (e.g. Compose requires significant super-additivity)."""
    nprk = cost / res_kills if res_kills else float('inf')
    if baseline:
        verdict = 'BASELINE'
    elif force_pass is not None:
        verdict = 'PASS' if force_pass else 'REJECT'
    else:
        verdict = 'PASS' if (killable > CEIL and nprk < BENCH) else 'REJECT'
    near = verdict == 'REJECT' and (nprk < 4 * BENCH or killable > CEIL / 2)
    rows.append(dict(family=family, params=params, killable=int(killable),
                     residual_kills=int(res_kills), cost=round(cost, 2),
                     nats_per_res_kill=round(nprk, 2) if res_kills else None,
                     verdict=verdict, near_miss=bool(near), reason=reason))
    return verdict


# ---- family 1: Congruence with composite / prime-power moduli (wp7-P1) ----
def sweep_congruence_composite():
    P = np.array(list(primerange(3, Q)), dtype=np.int64)
    mods = [d for d in range(4, 2000)
            if not sympy.isprime(d) and max(factorint(d)) < d]
    for d in mods[:400]:
        p = max(factorint(d))          # dominant prime factor
        res = P % d
        best = np.bincount(res, minlength=d).max()
        # subset property: class mod d is inside a class mod p at cost
        # ln d — INSIDE the covering paradigm (wp7-P1), never an escape
        emit('Congruence-composite', dict(d=d, vs=p), best, 0, math.log(d),
             f'class mod {d} subset of class mod {p}; cost ratio '
             f'{math.log(d)/math.log(p):.2f} for <= equal kills: dominated',
             baseline=True)


# ---- family 2: PolyImage N = a*m^k - c (wp7-P2 generalized) ----
def sweep_polyimage():
    for k in (2, 3, 4):
        fam_cost = (1 - 1 / k) * LNB
        for a in (1, 2, 3):
            cmax = 5000 if (k == 2 and a == 1) else 1500
            for c in range(1, cmax):
                killable = res = 0
                d = 2
                while a * d ** k - c < Q:
                    v = a * d ** k - c
                    if v > 2 and ISP[v]:
                        killable += 1
                        if v in RESIDUAL:
                            res += 1
                    d += 1
                if killable:
                    emit('PolyImage', dict(k=k, a=a, c=c), killable, res,
                         fam_cost, f'value set <= Q^(1/{k}); family cost '
                                   f'(1-1/{k})lnB')


# ---- family 3: ExpFamily N = j*a^n + c ----
def sweep_expfamily():
    svals = [s for s in primerange(500, 3000)][:40]
    for a in (2, 3, 5):
        for j in (1, 3, 5):
            for c in (-5, -1, 1, 5):
                # per-offset cost: cheapest certifying s gives ln(ord_s(a));
                # estimate kill fraction and mean cost over sample offsets
                qs = [q for q in range(max(3, c + 2), Q, 9973) if ISP[q]][:25]
                costs = []
                for q in qs:
                    best = None
                    for s in svals:
                        if (q - c) % s == 0 or a % s == 0 or j % s == 0:
                            continue
                        t = (q - c) * pow(j, -1, s) % s
                        o = n_order(a, s)
                        # t in <a> mod s iff t^o == 1
                        if pow(t, o, s) == 1:
                            best = min(best, math.log(o)) if best else math.log(o)
                    if best:
                        costs.append(best)
                if costs:
                    mean_c = sum(costs) / len(costs)
                    frac = len(costs) / len(qs)
                    kill_est = frac * len(RESIDUAL)
                    emit('ExpFamily', dict(a=a, j=j, c=c),
                         frac * (Q / math.log(Q)), kill_est,
                         mean_c * kill_est,
                         f'per-offset cost ~ln(ord)={mean_c:.1f}; one offset '
                         f'per condition (wp7-P3)')


# ---- family 4: MultiPoly binary quadratics + quartic products ----
def sweep_multipoly():
    x, y = sympy.symbols('x y', integer=True)
    seen = set()
    for a, b, c in itertools.product(range(-4, 5), repeat=3):
        if a <= 0 or (a, b, c) in seen:
            continue
        seen.add((a, b, c))
        f = a * x**2 + b * x * y + c * y**2
        disc = b * b - 4 * a * c
        red = sympy.sqrt(disc).is_integer if disc >= 0 else False
        if red:
            emit('MultiPoly-binquad', dict(a=a, b=b, c=c), 0, 0, 0.0,
                 'reducible: linear factors -> divisor O(range) -> '
                 'sieve-equivalent')
        else:
            emit('MultiPoly-binquad', dict(a=a, b=b, c=c), 0, 0, 0.0,
                 'irreducible: representation != compositeness')
    # quartic products A*B: measure enumeration work per certified offset
    forms = [((1, 0, 1), (1, 0, 2)), ((1, 1, 1), (1, 0, 1)),
             ((1, 0, 1), (2, 0, 3)), ((1, 1, 2), (1, 1, 1))]
    for (A, Bf) in forms:
        work = {}
        for X in (10**6, 10**8, 10**10):
            W = 10**4
            hits = 0
            T = int(X ** 0.25 * 2)
            for u in range(0, T):
                for v in range(0, T):
                    va = A[0]*u*u + A[1]*u*v + A[2]*v*v
                    if va == 0:
                        continue
                    vb = Bf[0]*u*u + Bf[1]*u*v + Bf[2]*v*v
                    m = va * vb
                    if X <= m < X + W and va > 1 and vb > 1:
                        hits += 1
            work[X] = (T * T, hits)
        # fit: enumeration points per certified hit vs height
        wph = {X: (t / h if h else float('inf')) for X, (t, h) in work.items()}
        xs = [X for X in wph if wph[X] != float('inf')]
        if len(xs) >= 2:
            lo, hi = min(xs), max(xs)
            expo = (math.log(wph[hi]) - math.log(wph[lo])) / \
                   (math.log(hi) - math.log(lo))
            reason = (f'enumeration work/hit ~ height^{expo:.2f} '
                      f'(measured {[f"{X:.0e}:{wph[X]:.0f}" for X in sorted(wph)]}); '
                      f'at 10^200 -> ~10^{200*expo:.0f} per offset')
        else:
            reason = f'no enumerable hits at heights {list(work)} (sliver empty)'
        emit('MultiPoly-quartic', dict(A=A, B=Bf), 0, 0, float('inf') if not xs
             else 200 * math.log(10) * expo, reason)


# ---- family 5: NormForm (reduces to family 4) ----
def sweep_normform():
    for D in [d for d in range(2, 200) if sympy.ntheory.primetest.is_square(d)
              is False][:60]:
        emit('NormForm', dict(disc=D), 0, 0, 0.0,
             'norm certificate = product of two norms = quartic-product '
             'case: enumeration wall (family 4); representation alone '
             'certifies nothing')


# ---- family 6: Cyclotomic / Aurifeuillian ----
def sweep_cyclotomic():
    for n in range(3, 201):
        phi = int(sympy.totient(n))
        if phi < 2:
            continue
        # value set of degree-phi polynomial below Q
        count = max(0, int(Q ** (1 / phi)) - 1)
        emit('Cyclotomic', dict(n=n, deg=phi), count,
             count * len(RESIDUAL) / (Q / math.log(Q)),
             (1 - 1 / phi) * LNB,
             f'univariate identity family deg {phi}: value-set ceiling '
             f'Q^(1/{phi})')


# ---- family 7: Compose depth 2 — additivity audit on samples ----
def sweep_compose(nsamples=60):
    rng = np.random.default_rng(5)
    P = np.array(list(primerange(3, Q)), dtype=np.int64)
    prs = [int(p) for p in primerange(3, 500)]
    for i in range(nsamples):
        r = int(rng.choice(prs))
        a = int(rng.integers(1, r))
        k = 2
        c = int(rng.integers(1, 3000))
        # congruence kills
        kill_a = int((P % r == a).sum())
        # poly kills among q == a mod r only (compose restricts family)
        kill_b = kill_joint = 0
        d = 2
        while d * d - c < Q:
            v = d * d - c
            if v > 2 and ISP[v]:
                kill_b += 1
                if v % r == a:
                    kill_joint += 1
            d += 1
        # contains a congruence component -> baseline paradigm; the only
        # escape would be SIGNIFICANT super-additive interaction:
        # overlap beyond expected + 3*sqrt(expected), with >= 5 events
        inter_pred = kill_b / max(r - 1, 1)
        sig = (kill_joint >= 5 and
               kill_joint > inter_pred + 3 * math.sqrt(max(inter_pred, 1)))
        emit('Compose', dict(r=r, a=a, c=c),
             kill_a + kill_b, 0, math.log(r) + 0.5 * LNB,
             f'joint overlap {kill_joint} vs expected {inter_pred:.1f}'
             + ('; SUPER-ADDITIVE (significant)' if sig
                else '; additive within Poisson noise'),
             baseline=not sig, force_pass=sig if sig else None)


if __name__ == '__main__':
    t0 = time.time()
    sweep_congruence_composite()
    sweep_polyimage()
    sweep_expfamily()
    sweep_multipoly()
    sweep_normform()
    sweep_cyclotomic()
    sweep_compose()
    passes = [r for r in rows if r['verdict'] == 'PASS']
    nears = [r for r in rows if r['near_miss']]
    json.dump(rows, open(os.path.join(HERE, 'exhaustive_results.json'), 'w'),
              indent=0, default=str)
    print(f"swept {len(rows)} schema instances in {time.time()-t0:.0f}s")
    print(f"PASSES: {len(passes)}")
    for r in passes:
        print("  !!", r)
    print(f"near-misses: {len(nears)}; top by nats/residual-kill:")
    nears.sort(key=lambda r: (r['nats_per_res_kill'] is None,
                              r['nats_per_res_kill']))
    for r in nears[:10]:
        print(f"   {r['family']} {r['params']} killable={r['killable']} "
              f"res={r['residual_kills']} cost={r['cost']} "
              f"n/rk={r['nats_per_res_kill']} :: {r['reason'][:70]}")
    fam_counts = {}
    for r in rows:
        fam_counts[r['family']] = fam_counts.get(r['family'], 0) + 1
    print("by family:", fam_counts)

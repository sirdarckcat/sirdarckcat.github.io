"""Door 1, D1.0: benchmark instance + landscape diagnostics at Q=122,000.

Outputs instance_q122k.json and prints: regret/stability distribution at
the greedy point vs random points; backbone overlap between independent
coordinate-ascent solutions (clustering diagnostic).
"""
import hashlib
import json
import math
import os

import numpy as np
from sympy import primerange

HERE = os.path.dirname(os.path.abspath(__file__))
PHD = os.path.dirname(os.path.dirname(HERE))
Q = 122000

spec = json.load(open(os.path.join(PHD, 'campaign3/base_spec.json')))
moduli = [int(r) for r, a in spec['cover']]
c1 = {int(r): int(a) for r, a in spec['cover']}
P = np.array(list(primerange(3, Q)), dtype=np.int64)
RES = {r: (P % r).astype(np.int32) for r in moduli}


def ucount(assign):
    cc = np.zeros(len(P), dtype=np.int16)
    for r in moduli:
        cc += (RES[r] == assign[r])
    return int((cc == 0).sum()), cc


def ascent(assign, rng=None):
    cc = np.zeros(len(P), dtype=np.int16)
    for r in moduli:
        cc += (RES[r] == assign[r])
    order = list(moduli)
    improved = True
    while improved:
        improved = False
        if rng is not None:
            rng.shuffle(order)
        for r in order:
            m = RES[r] == assign[r]
            cc -= m
            hist = np.bincount(RES[r][cc == 0], minlength=r)
            a = int(hist.argmax())
            if hist[a] > hist[assign[r]]:
                assign[r] = a
                improved = True
            cc += (RES[r] == assign[r])
    return assign, int((cc == 0).sum())


def stability(assign):
    """Per modulus: best-alternative gap (kills lost by switching to the
    best other class, given the rest). At a local optimum all gaps >= 0."""
    _, cc = ucount(assign)
    gaps = []
    for r in moduli:
        m = RES[r] == assign[r]
        cc2 = cc - m
        hist = np.bincount(RES[r][cc2 == 0], minlength=r)
        cur = hist[assign[r]]
        hist[assign[r]] = -1
        gaps.append(int(cur - hist.max()))
    return np.array(gaps)


if __name__ == '__main__':
    u0, _ = ucount(c1)
    inst = dict(Q=Q, moduli=moduli, c1_assignment=c1, baseline_U=u0,
                prime_universe=dict(count=len(P),
                                    sha256=hashlib.sha256(P.tobytes()).hexdigest()),
                boost=spec['boost'], nats_per_prime=spec['boost'] / (199 * math.log(10)))
    json.dump(inst, open(os.path.join(HERE, 'instance_q122k.json'), 'w'),
              indent=1)
    print(f"instance written; baseline |U| = {u0}")

    g = stability(dict(c1))
    print(f"stability gaps at c1 (greedy point): min={g.min()} "
          f"median={int(np.median(g))} max={g.max()}; "
          f"#tight(gap<=1)={int((g <= 1).sum())} of {len(g)}")

    rng = np.random.default_rng(17)
    sols = []
    for i in range(8):
        start = {r: int(rng.integers(1, r)) for r in moduli}
        a, u = ascent(start, rng)
        sols.append((u, a))
    us = sorted(u for u, _ in sols)
    print(f"8 random-start ascents: |U| = {us}")
    # backbone overlap: fraction of moduli sharing the same class
    ovl = []
    for i in range(8):
        for j in range(i + 1, 8):
            same = sum(sols[i][1][r] == sols[j][1][r] for r in moduli)
            ovl.append(same / len(moduli))
    print(f"pairwise class-agreement: mean={np.mean(ovl):.3f} "
          f"min={min(ovl):.3f} max={max(ovl):.3f}")
    ovl_c1 = [sum(a[r] == c1[r] for r in moduli) / len(moduli)
              for _, a in sols]
    print(f"agreement with c1: mean={np.mean(ovl_c1):.3f}")

"""WP9 engine, tier 0: calibration of the schema filter.

Must-reproduce targets (wp9_closure_theorem.md §6) before any scaling:
  T1  congruence anchor — greedy marginal cost/kill curve at Q=122,000
  T2  wp7-P2 reproduction — best m^k − c family below Q=10^5
      (expected ≈113 killable offsets at k=2, c=398) + live-cover
      residual relevance at Q=122,000
  T3  MultiPoly classification — irreducible forms certify nothing
      (representation ≠ compositeness); reducible forms' enumerable
      parameters map to bounded divisors (sieve-equivalence rule)
  T4  ExpFamily accounting — per-offset cost ln(ord_s(2)) vs plain
      congruence cost ln s for the same divisor (wp7-P3: no gain)

Each schema row: (schema, killable, design-cost nats, cost/offset,
verdict, reason).  PASS requires clearing the wp9 §5 triple; tier 0 is
expected to produce zero passes and to match wp7's hand numbers.
"""
import json
import math
import os
import sys
import time

import numpy as np
import sympy
from sympy import primerange, n_order

HERE = os.path.dirname(os.path.abspath(__file__))
PHD = os.path.dirname(os.path.dirname(HERE))
LNB = 200 * math.log(10)          # budget game at B = 10^200
ENDGAME_NATS = 2.5                # covering endgame benchmark (wp7-P2)


def prime_bitset(limit):
    s = np.ones(limit, dtype=bool)
    s[:2] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = False
    return s


# ---------------- T1: congruence anchor ----------------
def t1_congruence_anchor(Q=122000):
    spec = json.load(open(os.path.join(PHD, 'campaign3/base_spec.json')))
    moduli = [int(r) for r, a in spec['cover']]
    P = np.array(list(primerange(3, Q)), dtype=np.int64)
    cc = np.zeros(len(P), dtype=np.int16)
    rows = []
    for r in moduli:
        res = (P % r).astype(np.int64)
        hist = np.bincount(res[cc == 0], minlength=r)
        a = int(hist.argmax())
        kills = int(hist[a])
        rows.append((r, kills, math.log(r), math.log(r) / max(kills, 1)))
        cc += (res == a)
    print("T1 congruence anchor (greedy at Q=%d): last 6 moduli" % Q)
    for r, kills, cost, cpk in rows[-6:]:
        print(f"   r={r}: kills={kills} cost={cost:.2f} nats "
              f"-> {cpk:.2f} nats/offset")
    tail = rows[-6:]
    avg = sum(c for _, _, c, _ in tail) / sum(k for _, k, _, _ in tail)
    print(f"   endgame average: {avg:.2f} nats/offset "
          f"(benchmark {ENDGAME_NATS})")
    return {int(r): int(a) for r, a in spec['cover']}, P, cc


# ---------------- T2: wp7-P2 reproduction ----------------
def t2_poly_univariate(Q=100000, kmax=4, cmax=5000, live=None):
    isp = prime_bitset(Q + cmax + 10)
    best = {}
    for k in range(2, kmax + 1):
        top = (0, None)
        for c in range(1, cmax):
            d = 2
            n = 0
            while d ** k - c < Q:
                v = d ** k - c
                if v > 2 and isp[v]:
                    n += 1
                d += 1
            if n > top[0]:
                top = (n, c)
        best[k] = top
        fam_cost = (1 - 1 / k) * LNB
        n, c = top
        print(f"T2 m^{k}-c sweep (c<{cmax}, Q={Q}): best c={c} kills={n} "
              f"family cost={fam_cost:.0f} nats -> {fam_cost/max(n,1):.1f} "
              f"nats/offset  [wp7-P2: k=2 c=398 kills 113]")
    if live is not None:
        (cover, P, cc), Qlive = live
        isp2 = prime_bitset(Qlive + cmax + 10)
        residual = set(int(q) for q in P[cc == 0])
        k = 2
        fam_cost = (1 - 1 / k) * LNB
        n, c = best[k]
        kills_live = [d * d - c for d in range(2, int((Qlive + c) ** 0.5) + 2)
                      if 2 < d * d - c < Qlive and isp2[d * d - c]]
        res_kills = [q for q in kills_live if q in residual]
        print(f"T2 live relevance vs c1 (Q={Qlive}, best-total c={c}): "
              f"killable={len(kills_live)} of which residual="
              f"{len(res_kills)} -> {fam_cost/max(len(res_kills),1):.0f} "
              f"nats per residual kill (endgame benchmark {ENDGAME_NATS})")
        # residual-TARGETED sweep (wp7-P2's optimized figure ~5.8 n/kill)
        top = (0, None)
        for c2 in range(1, cmax):
            m = sum(1 for d in range(2, int((Qlive + c2) ** 0.5) + 2)
                    if 2 < d * d - c2 < Qlive and d * d - c2 in residual)
            if m > top[0]:
                top = (m, c2)
        m, c2 = top
        print(f"T2 residual-targeted sweep: best c={c2} residual kills={m} "
              f"-> {fam_cost/max(m,1):.1f} nats per residual kill "
              f"[wp7-P2 optimized: ~5.8]")
    return best


# ---------------- T3: MultiPoly classification ----------------
def t3_multipoly():
    x, y = sympy.symbols('x y', integer=True)
    forms = [x**2 - y**2, x**2 + y**2, x**2 + 3 * y**2,
             x**2 - 2 * y**2, 4 * x**2 - 9 * y**2, x**2 + x * y + y**2]
    print("T3 MultiPoly classification:")
    for f in forms:
        fl = sympy.factor_list(f)[1]
        red = any(sympy.total_degree(p) < sympy.total_degree(f)
                  for p, _ in fl) and len(fl) > 1 or \
              any(e > 1 for _, e in fl)
        if not red:
            print(f"   {f}: IRREDUCIBLE -> REJECT "
                  f"(representation != compositeness; primes are values)")
        else:
            # enumerable parameters |x|,|y| <= T give divisor values
            # |linear factor| = O(T): divisor <= sieve depth for any
            # poly-range T -> certificate subsumed by trial division
            print(f"   {f}: factors {[str(p) for p, _ in fl]} -> divisor = "
                  f"linear-form value = O(range) -> SIEVE-EQUIVALENT for "
                  f"enumerable ranges; balanced slice is the Fermat-"
                  f"factorization sliver (density -> 0). REJECT")


# ---------------- T4: ExpFamily accounting ----------------
def t4_expfamily(sample=8):
    print("T4 ExpFamily j*2^n+c: per-offset kill cost vs plain congruence:")
    rows = []
    for s in list(primerange(1000, 10 ** 6))[:0] or [1009, 10007, 100003, 999983]:
        o = n_order(2, s)
        rows.append((s, o, math.log(o), math.log(s)))
    for s, o, lo, ls in rows:
        print(f"   s={s}: ord_2(s)={o} -> cost ln(ord)={lo:.2f} vs "
              f"congruence ln(s)={ls:.2f} nats (same divisor s) "
              f"-> {'NO GAIN' if lo >= ls - 1e-9 else 'gain %.2f' % (ls-lo)}")
    print("   note: ord | s-1 so ln(ord) <= ln(s); apparent 'gain' buys a "
          "SINGLE offset per condition (the n-class), while the congruence "
          "class mod s kills ~pi(Q)/(s-1) offsets -> per-offset cost is "
          "ln(ord)/1 vs ln(s)/many: wp7-P3 verdict (reduces to covering) "
          "stands whenever pi(Q)/(s-1) >= ln(s)/ln(ord).")


if __name__ == '__main__':
    t0 = time.time()
    live = t1_congruence_anchor(122000)
    t2_poly_univariate(100000, kmax=3, cmax=5000, live=(live, 122000))
    t3_multipoly()
    t4_expfamily()
    print(f"tier-0 done in {time.time()-t0:.0f}s")

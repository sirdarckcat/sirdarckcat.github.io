"""Frontier experiments: what does a 1M Goldbach desert cost in digits?

Target: even N with g(N) > 10^6, i.e. every prime q <= 10^6 has N - q
composite.  The only known mechanism that forces compositeness of N - q
across many q at once is a congruence cover (r | N - q iff q == N mod r,
one residue class per prime r), so the whole question reduces to the
failure exponent

    E(D) = |U(D)| * boost(D) / ln(10^D)

of the best cover whose modulus fits in D digits: a random progression
element survives (all residual complements composite) with density e^-E,
so e^E is the number of candidates a search must scan.

This module measures E(D) at Q = 10^6 directly:

  * greedy_digit_cap -- lazy-greedy cover builder with a digit budget
    (cover.py's effective-gain score, priority-queue lazy evaluation so
    Q = 10^6 with hundreds of moduli stays fast);
  * residue_anneal   -- fixed-modulus-set annealing on |U| to polish the
    greedy residues (M and boost fixed, so minimizing E == minimizing |U|);
  * frontier         -- the E(D) table plus D_min solves for several
    search budgets;
  * blueprint        -- build + polish + save the cheapest practical
    1M-desert cover spec (the "what it would actually take" artifact);
  * toy              -- small-scale end-to-end validation: build a cover,
    search the progression, find a real desert N, compare measured hit
    density to predicted e^-E.
"""

import argparse
import heapq
import json
import math

import numpy as np
from sympy import primerange

import anneal as A
import cover as C

LN10 = math.log(10)


# --------------------------------------------------------------------------
# lazy-greedy cover with a digit budget
# --------------------------------------------------------------------------

def greedy_digit_cap(Q, digit_cap, rmax=30000, verbose=True):
    targets = np.array(list(primerange(3, Q)), dtype=np.int64)
    covered = np.zeros(len(targets), dtype=bool)
    chosen = {}
    logm = math.log(2)
    boost = 2.0

    def score(r):
        alive = targets[~covered]
        nU = len(alive)
        if nU == 0:
            return 0.0, 0
        cnt = np.bincount(alive % r, minlength=r)
        a = int(cnt.argmax())
        gain = int(cnt[a])
        eff = gain - (nU - gain) / (r - 1)
        return eff / math.log(r), a

    heap = []
    for r in primerange(3, rmax):
        s, a = score(int(r))
        heapq.heappush(heap, (-s, int(r), a))
    while heap:
        s_stale, r, a_stale = heapq.heappop(heap)
        if (logm + math.log(r)) / LN10 > digit_cap:
            continue                     # too big now; only grows -> drop
        s, a = score(r)
        if s <= 0:
            continue
        if heap and s < -heap[0][0]:     # stale: reinsert with fresh score
            heapq.heappush(heap, (-s, r, a))
            continue
        chosen[r] = a
        covered |= (targets % r) == a
        logm += math.log(r)
        boost *= r / (r - 1)
        if verbose and len(chosen) % 100 == 0:
            print(f"  greedy {len(chosen):4d} congr  M~{logm/LN10:7.1f}d  "
                  f"|U|={int((~covered).sum()):6d}", flush=True)
    return {"Q": Q, "chosen": chosen, "logm": logm, "boost": boost,
            "n_res": int((~covered).sum()), "n_targets": len(targets)}


# --------------------------------------------------------------------------
# residue-only annealing (modulus set fixed -> minimize |U|)
# --------------------------------------------------------------------------

def residue_anneal(Q, chosen, iters=40000, t0=6.0, t1=0.3, topj=4, seed=0,
                   verbose=True):
    import random
    st = A.State(Q, chosen, e_cap=1e9, ln_n=1.0)  # ln_n irrelevant: |U| only
    rng = random.Random(seed)
    rs = list(st.chosen)
    cur = st.n_res()
    best = (cur, dict(st.chosen))
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / max(iters - 1, 1))
        r = rng.choice(rs)
        cands = st.best_residues(r, topj=topj)
        if not cands:
            continue
        a_new = rng.choice(cands)[0]
        if a_new == st.chosen[r]:
            continue
        m = st.tmod(r)
        n_new = st.n_res() \
            + int(((st.cnt == 1) & (m == st.chosen[r])).sum()) \
            - int(((st.cnt == 0) & (m == a_new)).sum())
        if n_new < cur or rng.random() < math.exp((cur - n_new) / max(T, 1e-9)):
            st.apply_change(r, a_new)
            cur = n_new
            if cur < best[0]:
                best = (cur, dict(st.chosen))
        if verbose and it % 10000 == 0:
            print(f"  anneal it={it:6d} |U|={cur:6d} best={best[0]:6d}",
                  flush=True)
    return best


# --------------------------------------------------------------------------
# CLI commands
# --------------------------------------------------------------------------

def cmd_frontier(args):
    print(f"Q = {args.Q}  (targets: odd primes < Q); E at ln N = D*ln10")
    print(f"{'D':>6} {'moduli':>7} {'r_max':>7} {'m_dig':>7} {'|U|':>7} "
          f"{'boost':>6} {'E':>8}  {'search cost':>12}")
    rows = []
    for D in args.digits:
        res = greedy_digit_cap(args.Q, D, rmax=args.rmax, verbose=False)
        E = res["n_res"] * res["boost"] / (D * LN10)
        rows.append((D, res))
        cost = E / LN10  # log10 of e^E candidates
        print(f"{D:>6} {len(res['chosen']):>7} {max(res['chosen']):>7} "
              f"{res['logm']/LN10:>7.1f} {res['n_res']:>7} "
              f"{res['boost']:>6.2f} {E:>8.2f}  10^{cost:>6.1f} cand",
              flush=True)
    print("\nD_min estimates (linear interpolation on measured E(D)):")
    for e_budget, label in [(16.6, "record-scale search, 1.4e8 cand"),
                            (21.0, "heavy search, 1.3e9 cand"),
                            (25.0, "distributed, 7e10 cand"),
                            (68.0, "cosmological, 3e29 cand")]:
        Ds = [d for d, _ in rows]
        Es = [r["n_res"] * r["boost"] / (d * LN10) for d, r in rows]
        est = None
        for i in range(len(Ds) - 1):
            if Es[i] >= e_budget >= Es[i + 1]:
                f = (Es[i] - e_budget) / (Es[i] - Es[i + 1])
                est = Ds[i] + f * (Ds[i + 1] - Ds[i])
                break
        print(f"  E <= {e_budget:5.1f} ({label}): "
              f"D_min ~ {est:.0f} digits" if est else
              f"  E <= {e_budget:5.1f} ({label}): outside measured range")


def cmd_blueprint(args):
    res = greedy_digit_cap(args.Q, args.digits, rmax=args.rmax)
    E0 = res["n_res"] * res["boost"] / (args.digits * LN10)
    print(f"greedy: {len(res['chosen'])} moduli, M = {res['logm']/LN10:.1f}d, "
          f"|U| = {res['n_res']}, E = {E0:.2f}")
    n_best, chosen = residue_anneal(args.Q, res["chosen"], iters=args.iters,
                                    seed=args.seed)
    E = n_best * res["boost"] / (args.digits * LN10)
    print(f"anneal: |U| = {n_best}, E = {E:.2f}")
    covr = sorted((int(r), int(a)) for r, a in chosen.items())
    N0, M = C.crt(covr)
    targets = np.array(list(primerange(3, args.Q)), dtype=np.int64)
    cnt = np.zeros(len(targets), dtype=np.int16)
    for r, a in covr:
        cnt += (targets % r) == a
    residual = [int(q) for q in targets[cnt == 0]]
    spec = {"Q": args.Q, "cover": covr, "residual": residual,
            "boost": res["boost"], "m_digits": res["logm"] / LN10,
            "E": E, "n_digits_est": args.digits,
            "N0": str(N0), "M": str(M),
            "name": f"blueprint_q{args.Q}_d{args.digits}"}
    json.dump(spec, open(args.out, "w"))
    rate_hint = 50.0  # candidates/s per core at ~1000 digits (Fermat-bound)
    days = math.exp(E) / rate_hint / 86400
    print(f"expected search: e^E = {math.exp(E):.2e} candidates "
          f"~ {days:.0f} core-days at {rate_hint:.0f}/s")
    print("wrote", args.out)


def cmd_toy(args):
    res = C.build_cover(args.Q, e_target=args.e_target, rmax=args.rmax,
                        verbose=False)
    n_best, chosen = residue_anneal(args.Q, dict(res["cover"]),
                                    iters=args.iters, seed=args.seed,
                                    verbose=False)
    covr = sorted((int(r), int(a)) for r, a in chosen.items())
    N0, M = C.crt(covr)
    targets = np.array(list(primerange(3, args.Q)), dtype=np.int64)
    cnt = np.zeros(len(targets), dtype=np.int16)
    for r, a in covr:
        cnt += (targets % r) == a
    residual = [int(q) for q in targets[cnt == 0]]
    m_digits = len(str(M))
    D, E = C.self_consistent_D(math.log10(M), len(residual), res["boost"])
    spec = {"Q": args.Q, "cover": covr, "residual": residual,
            "boost": res["boost"], "m_digits": m_digits, "E": E,
            "n_digits_est": D, "N0": str(N0), "M": str(M),
            "kmax": args.kmax, "stop_on_success": False,
            "name": f"toy_q{args.Q}_d{m_digits}"}
    json.dump(spec, open(args.out, "w"))
    print(f"toy spec: Q={args.Q} moduli={len(covr)} M={m_digits}d "
          f"|U|={len(residual)} E={E:.2f} est-N~{D:.0f}d -> {args.out}")
    print(f"predicted hit density e^-E = {math.exp(-E):.3e} per k")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("frontier")
    p.add_argument("--Q", type=int, default=10**6)
    p.add_argument("--digits", type=int, nargs="+",
                   default=[199, 300, 400, 600, 800, 1000, 1300, 1600,
                            2000, 2400])
    p.add_argument("--rmax", type=int, default=30000)
    p.set_defaults(fn=cmd_frontier)

    p = sub.add_parser("blueprint")
    p.add_argument("--Q", type=int, default=10**6)
    p.add_argument("--digits", type=int, default=950)
    p.add_argument("--rmax", type=int, default=30000)
    p.add_argument("--iters", type=int, default=60000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="blueprint.json")
    p.set_defaults(fn=cmd_blueprint)

    p = sub.add_parser("toy")
    p.add_argument("--Q", type=int, default=6000)
    p.add_argument("--e-target", type=float, default=13.0)
    p.add_argument("--rmax", type=int, default=4000)
    p.add_argument("--iters", type=int, default=20000)
    p.add_argument("--kmax", type=int, default=3000000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="toy_spec.json")
    p.set_defaults(fn=cmd_toy)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

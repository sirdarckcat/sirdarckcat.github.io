"""F2 experiment: do successes concentrate at low surviving-residual k?

After sieving, each progression element k has a_k surviving residual
complements; success (all composite) has probability ~(1-p)^{a_k}, so
hits should tilt exponentially toward the low-a tail while the scanner
visits k in index order. This script scans a hit-rich toy spec
recording (a_k, success_k, tests_k) for every k, then reports:

  * the a-distribution of hits vs population;
  * expected Fermat-tests-to-first-hit for index-order vs
    ascending-a-order visiting (the payoff of a two-phase search).

Usage: exp_order.py spec.json kmax [sieve_b]
"""

import json
import math
import sys

import numpy as np

import search as S


def scan(spec, kmax, sieve_b=300000, block=16384):
    S.init_spec(spec, sieve_b, block)
    G = S.G
    M, U, cq = G["M"], G["U"], G["cq"]
    n0m, inv, Ssm, small = G["n0m"], G["inv"], G["S"], G["small"]
    Ss_list = G["S_small_list"]
    a_all, succ_all, tests_all = [], [], []
    from gmpy2 import powmod
    for k0 in range(0, kmax, block):
        alive = np.ones((len(U), block), dtype=bool)
        for i, q in enumerate(U):
            row = alive[i]
            kres = ((q - n0m) * inv - k0) % Ssm
            js = kres[small].tolist()
            for j, s in zip(js, Ss_list):
                row[j::s] = False
            jl = kres[~small]
            hit = jl < block
            row[jl[hit]] = False
        aliveT = np.ascontiguousarray(alive.T)
        counts = aliveT.sum(axis=1)
        for j in range(block):
            col = aliveT[j]
            ok = True
            t = 0
            for i in np.nonzero(col)[0]:
                n = cq[i] + (k0 + j) * M
                t += 1
                if powmod(2, n - 1, n) == 1:
                    ok = False
                    break
            a_all.append(int(counts[j]))
            succ_all.append(ok)
            tests_all.append(t)
    return np.array(a_all), np.array(succ_all), np.array(tests_all)


def main():
    spec = json.load(open(sys.argv[1]))
    kmax = int(sys.argv[2])
    sieve_b = int(sys.argv[3]) if len(sys.argv) > 3 else 300000
    a, succ, tests = scan(spec, kmax, sieve_b)
    hits = succ.nonzero()[0]
    print(f"scanned {len(a)} k: {len(hits)} hits; "
          f"a: mean {a.mean():.1f} sd {a.std():.1f}; "
          f"hit a: mean {a[succ].mean():.1f} sd {a[succ].std():.1f}")
    p_est = 1.0 / tests[~succ].mean()
    print(f"per-survivor prime prob p ~ {p_est:.3f}; "
          f"tilt prediction: hit mean shift = -p*sd^2 = "
          f"{-p_est * a.std()**2:.1f}")
    # deciles of a for hits vs population
    qs = np.quantile(a, np.linspace(0, 1, 11))
    hist_pop, _ = np.histogram(a, bins=qs)
    hist_hit, _ = np.histogram(a[succ], bins=qs)
    print("decile edges:", [int(x) for x in qs])
    print("pop per decile:", hist_pop.tolist())
    print("hits per decile:", hist_hit.tolist())
    # discovery-cost simulation: expected tests until first hit
    def cost_to_first(order):
        c = 0.0
        total = 0.0
        prob_no_hit = 1.0
        # deterministic replay: sum tests until first success in order
        for idx in order:
            total += tests[idx]
            if succ[idx]:
                return total
        return total
    idx_order = np.arange(len(a))
    asc = np.argsort(a, kind="stable")
    c_index = cost_to_first(idx_order)
    c_sorted = cost_to_first(asc)
    print(f"tests to first hit: index-order {c_index:.0f}, "
          f"ascending-a {c_sorted:.0f}, ratio {c_index/max(c_sorted,1):.2f}x")
    # bootstrap: average over random rotations to de-noise 'first hit'
    rng = np.random.default_rng(0)
    r_idx, r_srt = [], []
    for _ in range(200):
        rot = rng.integers(len(a))
        perm = np.roll(idx_order, rot)
        r_idx.append(cost_to_first(perm))
        srt = perm[np.argsort(a[perm], kind="stable")]
        r_srt.append(cost_to_first(srt))
    print(f"bootstrap mean tests-to-first-hit: index {np.mean(r_idx):.0f}, "
          f"sorted {np.mean(r_srt):.0f}, "
          f"gain {np.mean(r_idx)/max(np.mean(r_srt),1):.2f}x")


if __name__ == "__main__":
    main()

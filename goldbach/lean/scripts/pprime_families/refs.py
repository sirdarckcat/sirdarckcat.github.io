"""The reference rows: cover first and the ideal order (recomputed from the member file), a random sample scored at
depth 200, and the cover-first prefix scored at depth 200, by amount of work W (members scored)."""
import math, sys
import numpy as np
import pp

k1 = np.asarray(pp.K1); k2 = np.asarray(pp.K2); s = np.asarray(pp.SUCC)
print(f"# members {len(k1):,d}, successes {int(s.sum())}")
a = pp.examined(k1, s); b = pp.examined(k2, s)
print("# cover first, N examined for 1, 3, 10, 30 successes:", ", ".join(f"{a[t]:,.0f}" for t in pp.TARGETS), " (toy_compare: 2,982, 63,350, 253,380, 1,205,425)")
print("# ideal order, N examined:", ", ".join(f"{b[t]:,.0f}" for t in pp.TARGETS), " (toy_compare: 13, 401, 10,811, 73,849); gain in nats:",
      ", ".join(f"{math.log(a[t] / b[t]):.2f}" for t in pp.TARGETS))
rng = np.random.default_rng(1)
# cover-first prefix: members in increasing k1, random inside a level
order = np.lexsort((rng.random(len(k1)), k1))
print("\nwork W (members scored at depth 200) | method | members | successes in them | N examined for 1 | 3 | 10 | 30 | gain in nats over cover first at 1 | 3 | 10 | 30")
for W in (1000, 3000, 10000, 30000, 100000, 300000, 1000000, 3000000, 10000000, 30000000, len(k1)):
    idx = order[:W]
    ex = pp.examined(k2[idx], s[idx])
    g = [(math.log(pp.COVER[t] / ex[t]) if math.isfinite(ex[t]) else float('-inf')) for t in pp.TARGETS]
    print(f"{W:>11,d} | cover-first prefix, then depth 200 (largest k1 {int(k1[idx].max())}) | {W:,d} | {int(s[idx].sum())} | " +
          " | ".join(f"{ex[t]:,.0f}" if math.isfinite(ex[t]) else "-" for t in pp.TARGETS) + " | " + " | ".join(f"{x:+.2f}" if math.isfinite(x) else "-" for x in g))
    # random sample: average of the examined counts over 20 samples (median), successes mean
    exs = {t: [] for t in pp.TARGETS}; sc = []
    for rep in range(20 if W < len(k1) else 1):
        idx = rng.choice(len(k1), size=W, replace=False) if W < len(k1) else np.arange(len(k1))
        ex = pp.examined(k2[idx], s[idx]); sc.append(int(s[idx].sum()))
        for t in pp.TARGETS: exs[t].append(ex[t])
    med = {t: float(np.median(exs[t])) for t in pp.TARGETS}
    g = [(math.log(pp.COVER[t] / med[t]) if math.isfinite(med[t]) else float('-inf')) for t in pp.TARGETS]
    print(f"{W:>11,d} | random sample, then depth 200 (median of 20) | {W:,d} | {np.mean(sc):.1f} | " +
          " | ".join(f"{med[t]:,.0f}" if math.isfinite(med[t]) else "-" for t in pp.TARGETS) + " | " + " | ".join(f"{x:+.2f}" if math.isfinite(x) else "-" for x in g), flush=True)

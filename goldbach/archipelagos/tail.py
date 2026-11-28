# The extreme tail: model-predicted number of N with g(N) >= x (sum over N of (1-c)^u(N; x), sieve to Z)
# against the observed count, for x up to the window's record.  usage: python3 tail.py NAME [Z]
import sys, json
import numpy as np
from lib import *
name = sys.argv[1]; Z = int(sys.argv[2]) if len(sys.argv) > 2 else 65521
meta, g, isp, spf = load(name)
R = rough(spf, Z); c = float(np.asarray(isp).sum() / R.sum()); lc = np.log1p(-c)
gmax = int(g.max())
xs = sorted(set(int(v) for v in np.unique(np.percentile(g, [99, 99.9, 99.99, 99.999]).astype(int) + 1)) | {int(0.9 * gmax), gmax})
out = {"name": name, "Z": Z, "c": c, "gmax": gmax, "rows": []}
print(f"{name}: sieve to {Z}, c = {c:.4f}; window record g = {gmax}")
print(f"  {'x':>6} {'observed #N with g>=x':>22} {'model':>10} {'ratio':>7}")
for x in xs:
    u = count_rows(R, meta, rows_below(x))
    pred = float(np.exp(lc * u.astype(np.float64)).sum()); obs = int((g >= x).sum())
    out["rows"].append(dict(x=x, observed=obs, model=pred))
    print(f"  {x:>6} {obs:>22,} {pred:>10.2f} {obs / pred if pred else float('nan'):>7.3f}")
json.dump(out, open(f"tail_{name}.json", "w"), indent=1)

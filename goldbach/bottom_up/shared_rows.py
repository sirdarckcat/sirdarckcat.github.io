# Bottom-up round: families of nearby N that share tested rows (the archipelago mechanism: N + d reuses N - q when q and q + d are
# both prime). Members N0 + jD with D = 2*prod(shared moduli) < Q; only the moduli dividing D are a common cover. The best classes
# on those moduli are found by brute force. An integer N0 - m serves as a row of about mu = (Q/D)(D/phi(D))/ln Q members.
# The net is -(E - 36.46) + ln mu, against the 89-moduli baseline (1,502 rows, E = 36.46).
#   python3 shared_rows.py
import math, itertools
import numpy as np
Q = 200000; lnX = 200 * math.log(10)
s = np.ones(Q, bool); s[:2] = False
for i in range(2, int(Q ** 0.5) + 1):
    if s[i]: s[i * i::i] = False
rows = np.nonzero(s)[0]; rows = rows[rows > 2]
allmods = [3, 5, 7, 11, 13]; res = {r: rows % r for r in allmods}
for n in range(1, 6):
    mods = allmods[:n]; best = None
    for combo in itertools.product(*[range(1, r) for r in mods]):
        unc = np.ones(len(rows), bool)
        for r, a in zip(mods, combo): unc &= res[r] != a
        v = int(unc.sum())
        if best is None or v < best[0]: best = (v, combo)
    R = best[0]; D = 2 * math.prod(mods)
    p = 2 * math.prod(r / (r - 1) for r in mods) / lnX; E = -R * math.log(1 - p)
    phi = math.prod(r - 1 for r in mods); mu = (Q / D) * (D / phi) / math.log(Q); share = mu / (1 - math.exp(-mu))
    print(f"shared {mods}, D = {D}: rows {R}, E = {E:.1f} ({E - 36.46:+.1f}); members per tested integer {share:.1f} ({math.log(share):+.2f}); "
          f"net {-(E - 36.46) + math.log(share):+.1f} nats")

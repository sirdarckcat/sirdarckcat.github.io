# Brute force over the windows of every cover of first-order cost <= 1 (verifier), compared with my meet in the middle's files.
import time, pickle, numpy as np
from base import *
t0 = time.time()
dl = {r: dlt_table(r) for r in cprimes}
later = LATER[:8]; hit = {s: hit_table(s) for s in later}
gm = np.cumsum([int(hit[s].max()) for s in later])
zero = [(r, int(c)) for r in cprimes for c in np.nonzero(dl[r] == 0)[0] if c != cover[r]]
one = [(r, int(c)) for r in cprimes for c in np.nonzero(dl[r] == 1)[0]]
covers = [({}, 0)] + [({r: c}, 0) for r, c in zero] + [({r: c}, 1) for r, c in one] + [({r: c, r2: c2}, 1) for r, c in one for r2, c2 in zero if r2 != r]
print("covers of cost <= 1:", len(covers), "(cost 0:", sum(1 for _, c in covers if c == 0), ")")
SIG = {3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 8}
found = {j: {} for j in SIG}; members = 0
best_window = {j: 10**9 for j in SIG}
for ch, cost in covers:
    cls = dict(cover); cls.update(ch)
    na, mm = crt_pairs([(2, 0)] + [(r, cls[r]) for r in cprimes])
    Ka = (X - 1 - na) // M + 1; members += Ka
    tot = np.zeros(Ka, dtype=np.int16)
    for jj, s in enumerate(later, 1):
        pat = hit[s][(na % s + np.arange(s, dtype=np.int64) * (M % s)) % s].astype(np.int16)
        tot += np.resize(pat, Ka)
        if jj in SIG:
            defi = int(gm[jj - 1]) - tot
            best_window[jj] = min(best_window[jj], cost + int(defi.min()))
            for k in np.nonzero(defi <= SIG[jj] - cost)[0]:
                found[jj][na + int(k) * M] = (cost, int(defi[k]))
print(f"members scanned {members}   [{time.time() - t0:.1f}s]")
from collections import Counter
import glob
for jj in SIG:
    print(f"j={jj}: points with excess <= {SIG[jj]} in these windows: {len(found[jj])}; least excess over these windows {best_window[jj]}; by (cost, deficit): {dict(sorted(Counter(found[jj].values()).items()))}")
    for f in glob.glob(f"out_j{jj}_c{SIG[jj]}_l{SIG[jj]}_s{SIG[jj]}.pkl"):
        mm = pickle.load(open(f, "rb")); sub = {N for N, (c, d) in mm.items() if c <= 1}
        print(f"     my meet in the middle restricted to cost <= 1: {len(sub)}; identical sets: {sub == set(found[jj])}")
# smaller slack counts quoted on the page
for jj, sg in ((4, 1), (5, 2)):
    print(f"j={jj} sigma={sg}:", sum(1 for c, d in found[jj].values() if c + d <= sg))
print("j=7, the two cost-0 windows, members with deficit <= 6:", sum(1 for c, d in found[7].values() if c == 0))

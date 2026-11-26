# Rank the families of covers by what their small-modulus classes leave.
#
#   python3 family_search/frame_rank.py weights.txt m [top=200] [Q=170000]        (run from cover/)
#
# A frame is one nonzero class for each of the m smallest odd primes; the covers that share it are a family.  Printed:
# for every frame the weighted rows it leaves alive (weights.txt: "q weight", 64 = a full row) and the rows alive below
# Q, best first, and where the frame of family B stands.  Measured on 45 moduli (sublinear/README.md, "Families"): the
# number of complete covers of a family follows the rows its frame leaves alive with a correlation of -0.91 to -0.96.
import sys
import numpy as np
wfile, m = sys.argv[1], int(sys.argv[2]); top = int(sys.argv[3]) if len(sys.argv) > 3 else 200; Q = int(sys.argv[4]) if len(sys.argv) > 4 else 170000
W = np.loadtxt(wfile, dtype=np.int64); q, w = W[:, 0], W[:, 1].astype(float) / 64; below = q < Q
small = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41][:m]; res = {r: q % r for r in small}
B = {3: 2, 5: 3, 7: 5, 11: 6, 13: 5, 17: 4, 19: 10, 23: 4, 29: 21, 31: 13, 37: 20, 41: 1}
out = []
def rec(i, mask, frame):
    if i == m: out.append((float(w[mask].sum()), int((mask & below).sum()), tuple(frame))); return
    r = small[i]
    for a in range(1, r): rec(i + 1, mask & (res[r] != a), frame + [a])
rec(0, np.ones(len(q), dtype=bool), [])
out.sort(); v = np.array([o[0] for o in out]); kb = tuple(B[r] for r in small); ib = [o[2] for o in out].index(kb)
print(f"# {len(out)} frames on {small}; weighted rows alive: min {v.min():.1f} mean {v.mean():.1f} sd {v.std():.1f}; family B: {out[ib][0]:.1f} (rank {ib + 1}), rows alive below {Q}: {out[ib][1]}")
print("# rank | weighted rows alive | rows alive below Q | frame")
for i, (a, b, f) in enumerate(out[:top]): print(f"{i + 1} | {a:.2f} | {b} | " + " ".join(f"{r}:{c}" for r, c in zip(small, f)))

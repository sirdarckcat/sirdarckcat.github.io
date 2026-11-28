# Rows left at depth z for random members of one cover: mean, standard deviation, minimum over a sample.
# (The fourth column of the table in Result 3.)
#
#   python3 ../fscan/cover/make_specs.py 213070 best auto ../fscan/cover/starts/q213070_m89.txt best.json 1 1609
#   python3 member_depth.py best.json [members=20000]
import json, sys, random, math
import numpy as np
spec = json.load(open(sys.argv[1]))[0]
rows = np.array(spec["residual"], dtype=np.int64); N0 = int(spec["N0"]); M = int(spec["M"]); kmax = int(spec["kmax"])
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
depths = [1000, 2000, 5000, 20000, 50000]
ps = [int(p) for p in primes_upto(depths[-1]) if p > 463]
nm = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
random.seed(1); ts = np.array([random.randrange(kmax) for _ in range(nm)], dtype=np.int64)
alive = np.ones((nm, len(rows)), dtype=bool); out = {}
di = 0
for s in ps:
    while di < len(depths) and s > depths[di]:
        out[depths[di]] = alive.sum(axis=1).copy(); di += 1
    nres = (N0 % s + (ts % s) * (M % s)) % s            # N mod s for every member
    alive &= (rows % s)[None, :] != nres[:, None]
while di < len(depths): out[depths[di]] = alive.sum(axis=1).copy(); di += 1
print(f"cover with {len(rows)} rows at depth 463, {nm} random members")
for z in depths:
    c = out[z]; print(f"  depth {z:6d}: mean {c.mean():8.1f}  sd {c.std():6.2f}  minimum in the sample {c.min()}  (sd if rows were independent: {math.sqrt(len(rows) * (c.mean() / len(rows)) * (1 - c.mean() / len(rows))):.2f})")

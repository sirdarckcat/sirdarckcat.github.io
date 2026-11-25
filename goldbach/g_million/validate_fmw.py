# Cross-check of uarch's fmw kernel against gmpy2 on this scan's own members: for members already tested with gmpy2
# (tested_d1996.jsonl), replay the same shuffled order through fmw.Members.first_pass and compare the position of the first PRP.
import sys, json, random, time
sys.path.insert(0, "run/fermatw")                     # a copy of goldbach/fermatw from branch ccr-b8c25887-i6tn9f at 63f0b8d
import numpy as np, fmw
from gmpy2 import mpz
tag = "d1996"; nval = int(sys.argv[1]) if len(sys.argv) > 1 else 48
setup = json.load(open(f"setup_{tag}.json")); U = np.array(setup["rows_left"], dtype=np.uint32); idx = {int(q): i for i, q in enumerate(U.tolist())}
done = {}
for l in open(f"tested_{tag}.jsonl"):
    r = json.loads(l); done[r["k"]] = r
surv = {}
want = set(list(done)[:4 * nval])
for l in open(f"surv_{tag}.txt"):
    t = l.split(); k = int(t[0])
    if k in want: surv[k] = [int(v) for v in t[2:]]
ks = [k for k in done if k in surv][:nval]
rows, offs = [], [0]
for k in ks:
    order = list(surv[k]); random.Random(k).shuffle(order)
    rows += [idx[q] for q in order]; offs.append(len(rows))
M = fmw.Members(int(setup["N0"]), int(setup["D"]), U, 40_000_000)
print("L =", M.L, "available:", fmw.available())
t0 = time.time(); pos = M.first_pass(ks, rows, offs); dt = time.time() - t0
ok = 0; bad = []
for i, k in enumerate(ks):
    r = done[k]; exp = r["tests"] - 1 if not r.get("hit") else -1
    if pos[i] == exp: ok += 1
    else: bad.append((k, int(pos[i]), exp))
ntests = sum(int(p) + 1 for p in pos)
print(f"{len(ks)} members: {ok} agree with gmpy2 on the first PRP position, {len(bad)} differ {bad[:5]}; "
      f"{ntests} tests in {dt:.1f} s = {1000 * dt / ntests:.1f} ms per test (8 lanes, one core, machine loaded)")

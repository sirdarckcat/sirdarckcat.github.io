# Measure dumped covers on the weighted rows, as they are and with their last modulus replaced by other primes.
#
#   python3 family_search/family_eval.py weights.txt dump.txt tag [rmin=463] [rmax=590] [known=1308.67]     (run from cover/)
#
# dump.txt: "COVER k r:a ..." lines of a tempering run on the first 89 odd primes (3..463), e.g. PT_DUMP of ptcover.
# For every cover: its weighted rows W (weights.txt: "q weight", 64 = a full row; brainstorm/soft_weights.py), and, for
# every prime r in [rmin, rmax], W with 463 dropped and r added with its best class.  r <= 590 keeps a vector at least
# 2^24 members long below 10^200.  Printed: the best W as it is, the best over r, and the best for each r.  Covers
# within 2 weighted rows of `known` (the best cover known: family B on the 491 set, 1308.67 under weights_8.9days.txt)
# are written to <dump>.near_<tag>_r<r>.txt and polished with wdescend.py (output: that name + .out); anything below
# `known` is reported as CANDIDATE.
import os, subprocess, sys
import numpy as np
wfile, dump, tag = sys.argv[1], sys.argv[2], sys.argv[3]
rmin = int(sys.argv[4]) if len(sys.argv) > 4 else 463
rmax = int(sys.argv[5]) if len(sys.argv) > 5 else 590
known = float(sys.argv[6]) if len(sys.argv) > 6 else 1308.67
W = np.loadtxt(wfile, dtype=np.int64); q, w = W[:, 0], W[:, 1].astype(float) / 64
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
cands = [r for r in primes_upto(rmax) if r >= rmin]
rm = {}
def mod(r):
    if r not in rm: rm[r] = q % r
    return rm[r]
lines = []
for line in open(dump):
    t = line.split()
    if len(t) == 91 and t[0] == "COVER": lines.append(t)
lines.sort(key=lambda t: float(t[1])); seen = set(); best = (1e9, None); bestr = {r: (1e9, None) for r in cands}; near = []; n = 0
for t in lines[:40000]:
    key = " ".join(t[2:])
    if key in seen: continue
    seen.add(key); n += 1
    c = [tuple(map(int, x.split(":"))) for x in t[2:]]
    last_r, last_a = c[-1]
    cnt = np.zeros(len(q), dtype=np.int16)
    for r, a in c: cnt += mod(r) == a
    v = float(w[cnt == 0].sum())
    if v < best[0]: best = (v, key)
    u2 = (cnt - (mod(last_r) == last_a)) == 0; base = float(w[u2].sum()); head = " ".join(t[2:-1])
    for r in cands:
        g = np.bincount(mod(r)[u2], weights=w[u2], minlength=r); g[0] = 0
        a = int(np.argmax(g)); v2 = base - float(g[a])
        if v2 < bestr[r][0]: bestr[r] = (v2, f"{head} {r}:{a}")
        if v2 < known + 2.0: near.append((v2, f"{head} {r}:{a}"))
if not n: sys.exit(f"{tag}: no cover with 89 moduli in {dump}")
rb = min(cands, key=lambda r: bestr[r][0])
print(f"{tag}: {n} covers; best weighted rows as they are {best[0]:.2f}; best with another last prime: {bestr[rb][0]:.2f} (r = {rb}); "
      + " ".join(f"{r}:{bestr[r][0]:.1f}" for r in cands), flush=True)
if near:
    near.sort(); stem = f"{dump}.near_{tag.replace(' ', '_')}"
    byset = {}
    for v, key in near: byset.setdefault(key.split()[-1].split(":")[0], []).append((v, key))
    for r, items in sorted(byset.items(), key=lambda kv: kv[1][0][0])[:3]:           # polish the three best sets, one set of moduli at a time
        fr = f"{stem}_r{r}.txt"
        with open(fr, "w") as g:
            for v, key in items[:300]: g.write(f"COVER {int(-(-v // 1))} {key}\n")
        here = os.path.dirname(os.path.abspath(__file__))
        p = subprocess.run([sys.executable, f"{here}/wdescend.py", wfile, fr, fr + ".out", "2.0", "25", "2", "1", "200"], capture_output=True, text=True)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr.strip()[-200:]
        print(f"{tag}: r = {r}: {len(items[:300])} covers within 2 rows of {known}, polished: {last}", flush=True)
        try:
            if float(last.split()[1]) < known - 0.05: print(f"CANDIDATE below {known}: {fr}.out", flush=True)
        except Exception: pass

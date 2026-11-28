# Optimise inside one family: weighted tempering with the classes of the smallest moduli fixed.
#
#   python3 family_search/frame_search.py workdir weights.txt sweeps seed "3:2 5:3 7:5 11:6 13:5 17:4" [last=491] [known=1308.67]     (from cover/)
#
# The moduli are the odd primes up to 461 and `last`.  The frame's classes are fixed; the rows they strike are removed,
# ./ptcover_wfast (gcc -O3 -march=native -fopenmp -o ptcover_wfast ptcover_wfast.c -lm) optimises the other moduli on
# the rows left, and the best cover is put together and measured again from scratch: weighted rows, rows below 170,000.
# One line per call on standard output; "CANDIDATE" in front if the cover has fewer weighted rows than `known`
# (family B on the 491 set under family_search/weights_8.9days.txt).  Covers within 2 weighted rows of `known` are
# kept in workdir/near.txt as full "COVER k r:a ..." lines.
import os, subprocess, sys
import numpy as np
wd, wfile, sweeps, seed, frame = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
last = int(sys.argv[6]) if len(sys.argv) > 6 else 491; known = float(sys.argv[7]) if len(sys.argv) > 7 else 1308.67
os.makedirs(wd, exist_ok=True)
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
mods = [p for p in primes_upto(461) if p > 2] + [last]
fr = dict(tuple(map(int, t.split(":"))) for t in frame.split()); assert all(r in mods and 0 < a < r for r, a in fr.items())
W = np.loadtxt(wfile, dtype=np.int64); q, w = W[:, 0], W[:, 1]
alive = np.ones(len(q), dtype=bool)
for r, a in fr.items(): alive &= q % r != a
tag = "f" + "_".join(str(a) for a in fr.values()) + f"_s{seed}"
with open(f"{wd}/{tag}.w", "w") as f: f.write("".join(f"{a} {b}\n" for a, b in zip(q[alive], w[alive])))
with open(f"{wd}/{tag}.mod", "w") as f: f.write("".join(f"{r}\n" for r in mods if r not in fr))
dump = f"{wd}/{tag}.dump"
if os.path.exists(dump): os.remove(dump)
env = dict(os.environ, PT_DUMP=dump, PT_KDUMP=str(int(known + 2)))
run = subprocess.run(["./ptcover_wfast", f"{wd}/{tag}.w", f"{wd}/{tag}.mod", sweeps, seed, "betas56.txt"], env=env, capture_output=True, text=True)
best = [l for l in run.stdout.splitlines() if l.startswith("BEST")]
if not best: sys.exit(f"{tag}: tempering failed: {run.stderr[-300:]}")
def measure(cover):
    cnt = np.zeros(len(q), dtype=np.int16)
    for r, a in cover: cnt += q % r == a
    u = cnt == 0
    return float(w[u].sum()) / 64, int((u & (q < 170000)).sum())
free = [tuple(map(int, t.split(":"))) for t in best[0].split()[1:]]
cover = sorted(list(fr.items()) + free); assert [r for r, a in cover] == mods
wr, rows = measure(cover); line = " ".join(f"{r}:{a}" for r, a in cover)
near = 0
if os.path.exists(dump):
    seen = set()
    with open(f"{wd}/near.txt", "a") as g:
        for l in open(dump):
            t = l.split()
            if t and t[0] == "COVER" and " ".join(t[2:]) not in seen:
                seen.add(" ".join(t[2:])); c = sorted(list(fr.items()) + [tuple(map(int, x.split(":"))) for x in t[2:]]); v, _ = measure(c)
                if v < known + 2: near += 1; g.write(f"COVER {v:.2f} " + " ".join(f"{r}:{a}" for r, a in c) + "\n")
    os.remove(dump)
for ext in (".w", ".mod"): os.remove(f"{wd}/{tag}{ext}")
print(("CANDIDATE " if wr < known - 0.005 else "") + f"frame [{frame}] seed {seed} sweeps {sweeps}: weighted rows alive after the frame {float(w[alive].sum()) / 64:.1f}; best cover {wr:.2f} weighted rows, {rows} rows below 170,000; covers within 2 of {known}: {near}; COVER {wr:.2f} {line}", flush=True)

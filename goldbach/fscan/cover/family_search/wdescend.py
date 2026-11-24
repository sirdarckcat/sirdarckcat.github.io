# weighted record-to-record travel: capped walks (covergen, COVERGEN_WEIGHTS) at best + slack, restart from the best found
#   python3 family_search/wdescend.py weights.txt start_covers.txt out.txt [slack=2.0] [seconds=30] [rounds_without_gain=4] [threads=3] [keep=200]
# run from cover/ (it calls ./covergen); all covers of start_covers.txt must be on the same moduli.
import os, subprocess, sys, tempfile
import numpy as np
wf, start, out = sys.argv[1], sys.argv[2], sys.argv[3]
slack = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
secs = sys.argv[5] if len(sys.argv) > 5 else "30"
patience = int(sys.argv[6]) if len(sys.argv) > 6 else 4
threads = sys.argv[7] if len(sys.argv) > 7 else "3"
keep = int(sys.argv[8]) if len(sys.argv) > 8 else 200
W = np.loadtxt(wf, dtype=np.int64); q, w = W[:, 0], W[:, 1]; rmod = {}
def wrows(key):
    cov = np.zeros(len(q), dtype=bool)
    for x in key.split():
        r, a = map(int, x.split(":"))
        if r not in rmod: rmod[r] = q % r
        cov |= rmod[r] == a
    return int(w[~cov].sum())
pool = {}
for line in open(start):
    t = line.split()
    if t and t[0] == "COVER": pool[" ".join(t[2:])] = None
for k in pool: pool[k] = wrows(k)
tmp = tempfile.mkdtemp(); fail = 0; seed = 1
best = min(pool.values())
print(f"start: {len(pool)} covers, best {best/64:.3f} weighted rows", flush=True)
while fail < patience:
    top = sorted(pool.items(), key=lambda kv: kv[1])[:keep]
    f = os.path.join(tmp, "cur.txt")
    with open(f, "w") as g:
        for key, v in top: g.write(f"COVER {-(-v // 64)} {key}\n")
    cap = best / 64 + slack; seed += 1
    r = subprocess.run(["./covergen", "170000", f, f"{cap:.4f}", "100000000", str(seed)], capture_output=True, text=True,
                       env=dict(os.environ, COVERGEN_WEIGHTS=wf, OMP_NUM_THREADS=threads, COVERGEN_TIME=secs, COVERGEN_STALL=secs))
    lines = [l.split() for l in r.stdout.split("\n") if l.startswith("COVER")]
    if lines:
        kmin = min(int(t[1]) for t in lines)
        cand = [" ".join(t[2:]) for t in lines if int(t[1]) <= kmin + 1][:60000]
        for key in cand:
            if key not in pool: pool[key] = wrows(key)
    nb = min(pool.values())
    if nb < best: best = nb; fail = 0
    else: fail += 1
    pool = dict(sorted(pool.items(), key=lambda kv: kv[1])[:20000])
    print(f"walk {seed}: cap {cap:.2f}, {len(lines)} covers visited; best {best/64:.3f}; {sum(1 for v in pool.values() if v <= best + 32)} within half a row", flush=True)
with open(out, "w") as g:
    for key, v in sorted(pool.items(), key=lambda kv: kv[1]): g.write(f"COVER {-(-v // 64)} {key}\n")
print(f"best {best/64:.3f} weighted rows; {len(pool)} covers written to {out}")

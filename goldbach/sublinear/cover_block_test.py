# Block-type covers on the 89 moduli: the moduli t of a block (z, w] take the class N1 mod t of one common integer N1;
# the other moduli are then optimised by tempering on the rows the block leaves.  Control: the same block with random
# classes (the best of as many random vectors as N1 were tried).  Reports rows left below Q for the whole cover.
import sys, os, subprocess, numpy as np
C = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover"
Q = int(sys.argv[1]); sweeps = sys.argv[2]; NTRY = int(sys.argv[3]); blocks = [tuple(map(int, b.split("-"))) for b in sys.argv[4:]]
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
rows = primes(Q - 1); rows = rows[rows > 2]; mods = [int(p) for p in primes(463) if p > 2]
rng = np.random.default_rng(7)
def left_after(classes):
    alive = np.ones(len(rows), dtype=bool)
    for t, a in classes: alive &= rows % t != a
    return alive
def temper(alive, free, tag):
    with open(tag + ".w", "w") as f: f.write("".join(f"{q} 64\n" for q in rows[alive]))
    with open(tag + ".mod", "w") as f: f.write("".join(f"{r}\n" for r in free))
    run = subprocess.run([C + "/ptcover_wfast", tag + ".w", tag + ".mod", sweeps, "3", C + "/betas56.txt"], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1"))
    best = [l for l in run.stdout.splitlines() if l.startswith("BEST")][0]
    cov = [tuple(map(int, u.split(":"))) for u in best.split()[1:]]
    os.remove(tag + ".w"); os.remove(tag + ".mod")
    return cov
for z, w in blocks:
    B = [t for t in mods if z < t <= w]; free = [t for t in mods if not (z < t <= w)]
    res = {t: rows % t for t in B}
    # common integers
    n1s = rng.integers(Q, 50 * Q, size=NTRY); cnt = np.empty(NTRY, dtype=np.int64)
    for i, n1 in enumerate(n1s):
        alive = np.ones(len(rows), dtype=bool)
        for t in B: alive &= res[t] != int(n1 % t)
        cnt[i] = alive.sum()
    bi = int(cnt.argmin()); n1 = int(n1s[bi])
    # random classes on the block
    cr = np.empty(NTRY, dtype=np.int64); bestr = None
    for i in range(NTRY):
        cl = [int(rng.integers(1, t)) for t in B]; alive = np.ones(len(rows), dtype=bool)
        for t, a in zip(B, cl): alive &= res[t] != a
        cr[i] = alive.sum()
        if bestr is None or cr[i] < bestr[0]: bestr = (int(cr[i]), cl)
    print(f"Q={Q} block ({z}, {w}]: {len(B)} moduli. Rows left by the block alone: common integer mean {cnt.mean():.0f} sd {cnt.std():.0f} best {cnt.min()}; random classes mean {cr.mean():.0f} sd {cr.std():.0f} best {cr.min()}", flush=True)
    for name, classes in (("common integer %d" % n1, [(t, n1 % t) for t in B]), ("best random classes", list(zip(B, bestr[1])))):
        alive = left_after(classes); cov = temper(alive, free, f"t_{Q}_{z}_{w}")
        full = sorted(classes + cov); u = left_after(full)
        print(f"   {name}: block leaves {int(alive.sum())}; whole cover after tempering the other {len(free)} moduli: {int(u.sum())} rows left", flush=True)

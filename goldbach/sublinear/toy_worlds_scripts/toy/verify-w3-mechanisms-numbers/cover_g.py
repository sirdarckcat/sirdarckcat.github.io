# greedy covers in F_q[x], q = 2^k (verifier's own construction): usage k D n restarts seed
import sys, numpy as np, random, time
from ff2 import W
k = int(sys.argv[1]); D = int(sys.argv[2]); n = int(sys.argv[3]); restarts = int(sys.argv[4]); seed = int(sys.argv[5])
rng = random.Random(seed)
w = W(k)
rows = []; rdeg = []
irr = {}
d = 1; tot = 0
while tot < n:
    irr[d] = w.irreducibles(d); tot += d * len(irr[d]); d += 1
for dd in range(1, D + 1):
    if dd not in irr: irr[dd] = w.irreducibles(dd)
    rows += irr[dd]; rdeg += [dd] * len(irr[dd])
rdeg = np.array(rdeg)
# moduli: all irreducibles of the complete degrees that fit, then candidates of the next degree
full = []; room = n; dmod = 1
while dmod in irr and dmod * len(irr[dmod]) <= room and dmod <= max(irr):
    full += irr[dmod]; room -= dmod * len(irr[dmod]); dmod += 1
nextra = room // dmod
cands = irr[dmod] if nextra else []
print(f"F_{w.q}: rows of degree <= {D}: {len(rows)}; moduli: {len(full)} of degree < {dmod}, plus {nextra} of degree {dmod} (from {len(cands)}); total degree {sum(f.degree() for f in full) + nextra*dmod}; unused room {room - nextra*dmod}", flush=True)
def codes(pi):
    m = {}
    out = np.empty(len(rows), dtype=np.int32)
    for i, Q in enumerate(rows):
        s = str(Q % pi)
        out[i] = m.setdefault(s, len(m))
    return out, len(m)
t0 = time.time()
C = [codes(pi) for pi in full + cands]
print(f"residues done {time.time()-t0:.0f}s", flush=True)
nf = len(full)
def gain(i, alive):
    return np.bincount(C[i][0][alive], minlength=C[i][1])
best = None
for rs in range(restarts):
    order = list(range(nf)); rng.shuffle(order)
    alive = np.ones(len(rows), dtype=bool)
    cls = {}
    for i in order:
        g = gain(i, alive); c = int(g.argmax()); cls[i] = c; alive &= C[i][0] != c
    for e in range(nextra):
        bg = (-1, None, None)
        for i in range(nf, len(C)):
            if i in cls: continue
            g = gain(i, alive); c = int(g.argmax())
            if g[c] > bg[0]: bg = (int(g[c]), i, c)
        cls[bg[1]] = bg[2]; alive &= C[bg[1]][0] != bg[2]
    # improvement passes
    for ps in range(8):
        ch = False
        ids = list(cls); rng.shuffle(ids)
        for i in ids:
            cover_cnt = np.zeros(len(rows), dtype=np.int32)
            for j, c in cls.items():
                if j != i: cover_cnt += (C[j][0] == c)
            al = cover_cnt == 0
            cand_ids = [i] if i < nf else [j for j in range(nf, len(C)) if j == i or j not in cls]
            bg = (int(gain(i, al)[cls[i]]), i, cls[i])
            for j in cand_ids:
                g = gain(j, al); c = int(g.argmax())
                if g[c] > bg[0]: bg = (int(g[c]), j, c)
            if (bg[1], bg[2]) != (i, cls[i]):
                del cls[i]; cls[bg[1]] = bg[2]; ch = True
        if not ch: break
    alive = np.ones(len(rows), dtype=bool)
    for j, c in cls.items(): alive &= C[j][0] != c
    left = int(alive.sum())
    if best is None or left < best[0]:
        best = (left, dict(cls), alive.copy())
        print(f"  restart {rs}: rows left {left}; by degree {[int((alive & (rdeg == dd)).sum()) for dd in range(1, D+1)]}; {time.time()-t0:.0f}s", flush=True)
    if left == 0: break
print(f"BEST rows left {best[0]} of {len(rows)}")

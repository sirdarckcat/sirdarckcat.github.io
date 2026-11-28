# exact row counts for Theorem 1 / Corollary (verifier's own code)
# usage: k Aspec lamidx degs [sample seed]   Aspec like L2, L2*x, V3, L1*x
import sys, random, time
from ff2 import W, predicted
k = int(sys.argv[1]); spec = sys.argv[2]; lamidx = int(sys.argv[3])
degs = [int(t) for t in sys.argv[4].split(',')]
sample = int(sys.argv[5]) if len(sys.argv) > 5 else 0
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 12345
rng = random.Random(seed)
w = W(k); F = w.F; x = w.x
A = w.R([1])
for part in spec.split('*'):
    if part[0] == 'L': A = A * w.L(int(part[1:]))
    elif part[0] == 'V': A = A * w.V(int(part[1:]))
    elif part == 'x': A = A * x
    else: raise SystemExit('spec')
lam = w.els[lamidx]
N = lam * A**4
a = A.degree(); n = 4*a
print(f"F_{w.q}: A = {spec}, a = {a}, n = {n}, lam = {lam}", flush=True)
radA = A.radical() if hasattr(A, 'radical') else None
for d in degs:
    t0 = time.time()
    if sample and w.q**d > 300000:
        rows = []; seen = set()
        while len(rows) < sample:
            Q = w.rand_monic(d, rng)
            s = str(Q)
            if s in seen or not Q.is_irreducible(): continue
            seen.add(s); rows.append(Q)
        total = (w.q**d)  # not the count
        note = f"(random sample of {sample} irreducibles)"
    else:
        rows = w.irreducibles(d)
        note = ""
        if sample and len(rows) > sample:
            note = f"(random sample of {sample} of {len(rows)})"
            rows = rng.sample(rows, sample)
    cat = {}
    bad = 0; even = 0; irr = 0
    for Q in rows:
        f = N - Q
        r, sqf = w.nfac(f)
        if r == 1: irr += 1
        pr = predicted(w, lam, A, Q, 1)
        S = w.S_of(Q)
        c = Q.coeffs()
        if pr is not None:
            lab = 'formula'
            if pr != r % 2: bad += 1
        elif not (A % S).is_zero():
            lab = 'S!|A,rad|A' if (A % S.radical()).is_zero() else 'S!|A,rad!|A'
        elif d % 2 == 0 and c[d-1] == F(0):
            lab = 'q_{d-1}=0'
        else:
            lab = 'other'
        e = cat.setdefault(lab, [0,0]); e[r % 2] += 1
        if r % 2 == 0: even += 1
    print(f"  d = {d}: rows {len(rows)} {note}; r even {even}; irreducible N-Q {irr}; [even,odd] by category {cat}; formula disagreements {bad}; {time.time()-t0:.0f}s", flush=True)

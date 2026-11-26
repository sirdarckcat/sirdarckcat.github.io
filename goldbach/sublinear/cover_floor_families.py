#!/usr/bin/env python3
"""The families' shares of the samples of a cover_floor run made with COVER_FLOOR_FAMILIES=6.

    python3 cover_floor_families.py run.txt [beta ...]

A family is the set of class vectors with the same frame, here the classes of the six smallest moduli 3..17.  In
equilibrium the share of a family among the samples at beta is Z_family(beta)/Z(beta); printed for the twelve most
visited families at each chosen temperature, with the family's own floor -ln Z_family/beta and the fewest rows seen in
it, and for the two families named in ../fscan/cover/README.md (family B and the runner-up of the plain search).
"""
import sys, math
import cover_floor as cf
path = sys.argv[1]; want = [float(v) for v in sys.argv[2:]] or [0.99, 1.15, 1.31, 1.5, 1.72, 2.0]
par, reps = cf.analyse(path); lnZ = {round(r["beta"], 4): r for r in reps}
small = [3, 5, 7, 11, 13, 17]
def decode(i):
    out = []
    for r in reversed(small): out.append(i % r); i //= r
    return tuple(reversed(out))
B = (2, 3, 5, 6, 5, 4); B2 = (2, 3, 5, 4, 6, 4)
for line in open(path):
    if not line.startswith("FAM"): continue
    t = line.split(); beta = float(t[1])
    if not any(abs(beta - w) < 1e-6 for w in want): continue
    ent = [(decode(int(a)), int(b), float(c)) for a, b, c in (u.split(":") for u in t[5:])]
    r = lnZ[round(beta, 4)]; n = r["n"]; tot = sum(e[1] for e in ent)
    print(f"beta {beta:.2f}: {t[3]} frames visited; the 300 most visited hold {tot / n:.3f} of the samples; ln Z = {r['lnZ']:.2f}, floor {r['floor']:.2f}, <k> {r['mean']:.1f}")
    for rank, (fr, c, lo) in enumerate(ent[:12]):
        tag = " (family B)" if fr == B else " (runner-up)" if fr == B2 else ""
        print(f"   {rank + 1:3d}. " + " ".join(f"{m}:{a}" for m, a in zip(small, fr)) + f"  share {c / n:.4f}  family floor {-(r['lnZ'] + math.log(c / n)) / beta:.2f}  lowest seen {lo:.2f}{tag}")
    for name, key in (("family B", B), ("runner-up", B2)):
        pos = [i for i, e in enumerate(ent) if e[0] == key]
        if pos and pos[0] >= 12: e = ent[pos[0]]; print(f"   {pos[0] + 1:3d}. {name}: share {e[1] / n:.5f}  family floor {-(r['lnZ'] + math.log(e[1] / n)) / beta:.2f}  lowest seen {e[2]:.2f}")
        if not pos: print(f"   {name}: not among the 300 most visited")

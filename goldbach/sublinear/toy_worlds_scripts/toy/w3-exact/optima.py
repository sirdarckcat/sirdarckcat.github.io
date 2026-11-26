# the optima of an instance: N as a polynomial, derivative, translation invariance, factorisation of N
import sys, re
from gfcommon import World, ftype
fn = sys.argv[1]; q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:]); k = int(sys.argv[2]) if len(sys.argv) > 2 else 6
W = World(q); x = W.x
top = []; dtop = []
for line in open(fn):
    t = line.split()
    if t[0] == "TOP": top.append((int(t[1]), int(t[2])))
    if t[0] == "DTOP": dtop.append(int(t[1]))
    if t[0] == "Gmax": print(f"q={q} n={n}: {line.strip()}")
def inv_group(N):
    return [b for b in range(q) if N(x + W.el[b]) == N]
for v, G in top[:k]:
    N = W.poly(v, n); dN = N.derivative()
    print(f"  G={G}  v={v}  N = {N}\n      deg N' = {dN.degree()}  N' = {dN}   translations fixing N: {inv_group(N)}   type of N: {ftype(N)[0]}")
ninv = sum(1 for v in dtop if len(inv_group(W.poly(v, n))) > 1)
print(f"  D = Dmax list: {len(dtop)} N listed, of which fixed by a nontrivial translation: {ninv}")

# per derivative class: number of N, and the fraction with D >= d for the top degrees
import sys, re, collections
fn = sys.argv[1]; q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:])
DH = collections.defaultdict(collections.Counter)
for line in open(fn):
    t = line.split()
    if t[0] == "DH": DH[int(t[1])][int(t[2])] += int(t[3])
Dmax = max(d for c in DH for d in DH[c])
print(f"q={q} n={n}; columns: class (deg N'), count, then #D>=d and rate for d = {list(range(max(2, Dmax - 3), Dmax + 1))}")
allc = collections.Counter()
for c in DH:
    if c <= n: allc.update(DH[c])
def row(name, C):
    tot = sum(C.values()); s = f"  {name:>6} {tot:>10}"
    for d in range(max(2, Dmax - 3), Dmax + 1):
        k = sum(v for dd, v in C.items() if dd >= d); s += f"   {k:>9} {k / tot:.3e}"
    print(s)
row("all", allc)
for c in sorted(DH): row("N'=0" if c == 0 else "N'=1" if c == n + 1 else str(c - 1), DH[c])

import sys, collections, math
fn, q, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); tot = q ** n
B = collections.defaultdict(list)
for line in open(fn):
    t = line.split()
    if t[0] == "BIN": B[int(t[1])].append(tuple(int(v) for v in t[2:]))
bl = B[1]; c = sum(b[2] for b in bl); H = sum(b[3] for b in bl)
ms = sum(b[0] * b[2] for b in bl) / c; mo = sum(b[1] * b[2] for b in bl) / c
ss = math.sqrt(sum((b[0] - ms) ** 2 * b[2] for b in bl) / c); so = math.sqrt(sum((b[1] - mo) ** 2 * b[2] for b in bl) / c)
opt = [(b[0], b[1]) for b in bl if b[3]]
print("hits", H, "s mean %.2f sd %.2f; o mean %.2f sd %.2f; optimum (s,o):" % (ms, ss, mo, so), opt)
blind = (tot + 1) / (H + 1)
for nm, key in (("rows left", 0), ("odd rows left", 1)):
    agg = collections.Counter(); hit = collections.Counter()
    for b in bl: agg[b[key]] += b[2]; hit[b[key]] += b[3]
    cum = 0
    for k in sorted(agg):
        if hit[k]: w = cum + (agg[k] + 1) / (hit[k] + 1); break
        cum += agg[k]
    print(f"rank by {nm}: expected work {w:.0f} against blind {blind:.0f}: {math.log(blind / w):.2f} nats")

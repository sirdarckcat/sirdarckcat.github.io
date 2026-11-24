import re, sys
pat = re.compile(r"^(\S+Z) batch .*?expected near>=(\d+) (\S+?),")
a, b = sys.argv[2], sys.argv[3]; s = 0.0; n = 0
for l in open(sys.argv[1]):
    m = pat.match(l)
    if m and a <= m.group(1) < b and m.group(2) == "158209":
        s += float(m.group(3)); n += 1
print(f"[ns] {sys.argv[1]} {a}..{b}: {n} batches, expected near-misses >= 158,209: {s:.4f}")

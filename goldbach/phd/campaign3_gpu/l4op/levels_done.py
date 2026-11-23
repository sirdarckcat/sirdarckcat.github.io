# The lead's item 8 ledger (23 Nov 18:41Z): which levels of k were done for each m88f vector, from a campaign's search.log (one line a slice: [name@k0] k=[k0, k0 + 2^25)).
# Levels count from the top: level j covers [2^32 - j * 2^25, 2^32 - (j - 1) * 2^25). With KLO = 2^32 - 16 * 2^25 a vector is finished at 16 levels.
#   python3 levels_done.py CAMPAIGN_DIR [--list]   (--list: one line a vector: name, number of levels, the levels)
import collections, re, sys
D = sys.argv[1]; S = 1 << 25; TOP = 1 << 32
lv = collections.defaultdict(set)
for l in open(D + "/search.log"):
    m = re.match(r"\[(\S+)@(\d+)\] k=\[", l)
    if m:
        lv[m.group(1)].add((TOP - int(m.group(2))) // S)
c = collections.Counter(len(v) for v in lv.values())
top16 = sum(1 for v in lv.values() if set(range(1, 17)) <= v)
print(f"[lv] {D}: {len(lv)} vectors with slices | levels a vector: {dict(sorted(c.items()))} | all of the top 16 done: {top16} | slices {sum(len(v) for v in lv.values())}")
if "--list" in sys.argv:
    for n in sorted(lv):
        print(n, len(lv[n]), ",".join(map(str, sorted(lv[n]))))

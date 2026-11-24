# Every found / near-miss line on this card, for found_sync.sh: the campaign dirs' found.jsonl and the CPU shares' found files, one "[fd] path<TAB>line" a line.
import glob, os
for f in sorted(set(glob.glob("/content/c1*/found.jsonl") + glob.glob("/content/c150cpu/goldbach/phd/campaign3_hi*/found.jsonl"))):
    for l in open(f):
        if l.strip():
            print("[fd]", f, "\t", l.strip(), sep="")
print("[fd-end]", os.popen("hostname").read().strip())

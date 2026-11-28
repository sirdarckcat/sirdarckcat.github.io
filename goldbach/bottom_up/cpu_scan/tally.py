# Tally a search_c.py scan from its worker logs: covers, members, Fermat tests, core-seconds, finds, and the expected number of
# finds (the sum over covers of K * e^-E^ * hit%, from each summary line).
#   python3 tally.py <scan directory> <log prefix>      e.g. python3 tally.py /home/user/cpu_scan_f613 f613_w
import sys, glob, re, math, os
d, pre = sys.argv[1], sys.argv[2]
pat = re.compile(r"^\[(c\d+_r\d+)\] k=\[(\d+),(\d+)\) (\d+)s .* tests=(\d+) prp=(\d+) p\^=([\d.]+) alive/k=([\d.]+) E\^=([\d.]+) hit%=([\d.]+) found=(\d+)")
cov = mem = tests = secs = found = 0; names = set()
for f in sorted(glob.glob(os.path.join(d, pre + "*.log"))):
    for l in open(f):
        m = pat.match(l)
        if not m: continue
        name, k0, k1, s, t = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        if name in names: continue
        names.add(name); cov += 1; mem += k1 - k0; tests += t; secs += s; found += int(m.group(11))
finds = sum(1 for f in glob.glob(os.path.join(d, "*found*.jsonl")) for l in open(f) if l.strip())
print(f"{d}: {cov} covers, {mem:.4g} members, {tests:.4g} Fermat tests, {secs/3600:.1f} core-hours, found {found} (find files: {finds} lines)")

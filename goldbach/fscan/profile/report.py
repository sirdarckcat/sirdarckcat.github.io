#!/usr/bin/env python3
"""report.py samples.txt binary source.c [topN]

Maps the samples of sampler.c to source lines with addr2line (the binary must be built with -g -no-pie) and prints the share of
the samples for each line of fscan.c and fermat*.h (the innermost line that is not a compiler intrinsic header), most frequent
first, then the share of the main stages.  Samples in the vector enumeration (pcw, dfs) are listed too: with a slice= run each
slice walks the whole enumeration, so they are over-represented compared with a production scan, which is why the stage
shares below are also given without them."""
import collections, os, re, subprocess, sys

samples = open(sys.argv[1]).read().split("\n")
total = int(samples[0].split()[1])
entries = [(int(a, 16), int(c)) for a, c in (l.split() for l in samples[1:] if l.strip())]
binary, src = sys.argv[2], sys.argv[3]
topn = int(sys.argv[4]) if len(sys.argv) > 4 else 40
entries = [(a, c) for a, c in entries if 0x400000 <= a < 0x1000000]
res = subprocess.run(["addr2line", "-e", binary, "-f", "-C", "-i", "-a"] + [hex(a) for a, _ in entries], capture_output=True, text=True).stdout.split("\n")
blocks, cur, i = [], None, 0
while i < len(res):
    l = res[i]
    if re.fullmatch(r"0x[0-9a-f]+", l):
        cur = []; blocks.append(cur)
    elif l.strip() and i + 1 < len(res):
        cur.append((l, res[i + 1])); i += 1
    i += 1
bysrc = collections.Counter(); stages = collections.Counter()
KERNEL = ("f52_run", "fm_run", "fm3_run", "fm4_run")
SETUP = ("f52_setup", "fm3_setup", "fm4_setup", "fm_exp_words", "fm_inv_neg", "fm_bitlen", "f52_test", "fm_test")
def stage_of(frames, key):
    names = [f for f, _ in frames]
    if any(n in KERNEL for n in names): return "Fermat kernel (squarings and the verdicts)"
    if any(n in SETUP for n in names): return "Fermat setup of each number"
    if "fermat_drain" in names: return "Fermat drain (refill, rows, results)"
    if "exact_stage" in names: return "exact stage"
    if "scan_vector" in names:
        t = ""
        fn, ln = key
        L = cache_lines(fn)
        if 0 < ln <= len(L): t = L[ln - 1]
        if "vb_adds" in t or "vb_loadu" in t or "ow[" in t or "const u8 *t = " in t or "offs" in t or "phi" in t or "DLT" in t or "CKMv" in t:
            return "score loop and window offsets"
        return "selection, exp/log, queue, table setup (scan_vector glue)"
    if "pcw" in names or "dfs" in names or "collect" in names or "main" in names: return "vector enumeration (an artifact of slice=)"
    return "other"
srcdir = os.path.dirname(os.path.abspath(src)); cache = {}
def cache_lines(fn):
    if fn not in cache:
        p = os.path.join(srcdir, fn); cache[fn] = open(p).read().split("\n") if os.path.exists(p) else []
    return cache[fn]
for (a, c), frames in zip(entries, blocks):
    key = ("?", -1)
    for f, l in frames:
        if "intrin.h" in l: continue
        m = re.search(r"([\w.]+):(\d+)", l)
        if m and ("fscan" in m.group(1) or "fermat" in m.group(1) or "fm_common" in m.group(1)):
            key = (m.group(1), int(m.group(2))); break
    bysrc[key] += c
    stages[stage_of(frames, key)] += c
def text(fn, ln):
    L = cache_lines(fn); return L[ln - 1].strip()[:84] if 0 < ln <= len(L) else "?"
scan = sum(c for k, c in stages.items() if not k.startswith("vector enumeration"))
print("\nstage shares of all samples / of the samples outside the enumeration:")
for k, c in stages.most_common(): print(f"  {100 * c / total:6.2f}%  {'' if k.startswith('vector enumeration') else f'{100 * c / scan:6.2f}%'}  {k}")

print(f"\ntotal samples {total}; the most frequent source lines:")
for (fn, ln), c in bysrc.most_common(topn):
    print(f"{100 * c / total:6.2f}%  {fn}:{ln:<4d} {text(fn, ln)}")

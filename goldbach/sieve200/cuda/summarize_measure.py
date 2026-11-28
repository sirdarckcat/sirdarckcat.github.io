#!/usr/bin/env python3
"""A compact table from the output files of measure_all.sh (one per GPU):

    python3 summarize_measure.py measure_rtxpro6000_sections1-6.txt measure_l4_sections1-6.txt ...

Prints, per file: the GPU, the Fermat kernels' tests/s with the SM clock and power, the global-memory rates, ns a mark of the large-prime stage at each bound (total, gen, apply, pass B),
the best row of the sieve sweep, and the whole batch pipeline's per-phase times.  It only reads text, so it runs anywhere.
"""
import re
import sys


def summarize(path):
    t = open(path, errors="replace").read()
    name = re.search(r"^(NVIDIA [^\n]*?)(?:  \(|: \d+ rows|\s*$)", t, re.M)
    print(f"=== {path}")
    m = re.search(r"\n([^\n,]+), ([\d.]+), (\d+) MiB, P\d, ([\d.]+) W, ([\d.]+) W, (\d+) MHz", t)
    if m:
        print(f"  GPU {m.group(1)}: {int(m.group(3)) / 1024:.0f} GB, power limit {m.group(4)} W (max {m.group(5)}), max SM clock {m.group(6)} MHz")
    for v in re.finditer(r"  (s1r_asm|s1rw|s1_asm|s1w|s1)\s+regs\s+(\d+) local\s+(\d+) B: median\s+([\d,]+) tests/s.*?\n.*?SM clock MHz: median (\d+) +min (\d+) +max (\d+).*?\n\s+power W: median (\d+)", t, re.S):
        print(f"  Fermat {v.group(1):8s} {int(v.group(4).replace(',', '')) / 1e6:6.2f}M tests/s, {v.group(2)} regs, SM clock median {v.group(5)} MHz (min {v.group(6)}), {v.group(8)} W")
    g = re.search(r"scattered atomicAnd.*?\n.*?scattered plain store[^\n]*\n[^\n]*scattered load[^\n]*\n[^\n]*128 B runs[^\n]*", t)
    if g:
        for line in g.group(0).split("\n"):
            print("  " + re.sub(r"\s{2,}", "  ", line.strip()))
    for blk in re.finditer(r"primes in \(2\^(\d+), 2\^(\d+)\][^\n]*\n.*?TOTAL ([\d.]+)[^\n]*\n[^\n]*ns a member of the batch: ([\d.]+)[^\n]*\n[^\n]*pass B[^\n]*?= ([\d.]+) ns a mark", t, re.S):
        mm = re.search(r"ns a mark: gen ([\d.]+)\s+apply ([\d.]+)", blk.group(0))
        print(f"  large primes up to 2^{blk.group(2)}: {blk.group(3)} ns a mark (gen {mm.group(1)}, apply {mm.group(2)}, pass B {blk.group(5)}), {blk.group(4)} ns a member of a 2^25 batch")
    sw = re.findall(r"\{[^}]*\}\s+([\d.]+)\s+([\d.]+) \|\s+([\d.]+)\s+([\d.]+)", t)
    rows = re.findall(r"(\{[^}]*\})\s+([\d.]+)\s+([\d.]+) \|", t)
    if rows:
        best = min(rows, key=lambda r: float(r[2]))
        base = rows[0]
        print(f"  sieve sweep (K = 2^19): production kernel {base[0]} {base[2]} ns a member; best {best[0]} {best[2]} ns a member")
    b = re.search(r"wall ([\d.]+) ms = ([\d.]+) ns a member[^\n]*\n\s+prep ([\d.]+)\s+sieve \(gen \+ tiles\) ([\d.]+)\s+count ([\d.]+)\s+select ([\d.]+)\s+finalize ([\d.]+)\s+wait1 ([\d.]+)\s+rows ([\d.]+)\s+wait2 ([\d.]+)", t)
    if b:
        print(f"  whole 2^25 batch at the deep bound: {b.group(1)} ms = {b.group(2)} ns a member: sieve {b.group(4)}, count {b.group(5)}, select {b.group(6)}, finalize {b.group(7)}, rows {b.group(9)} ms")
    for f in re.findall(r"FAILED[^\n]*", t):
        print("  " + f)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        summarize(p)

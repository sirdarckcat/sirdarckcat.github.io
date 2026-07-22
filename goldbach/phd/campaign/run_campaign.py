"""Restart-safe driver for the E10 campaign, v2: interleaved k-slices.

The session container can be reclaimed at any idle moment, so the campaign
is cut into small work units: each variant's k-range [0, 1.5e6) is split
into slices of SLICE k (8 sieve blocks, ~2 min each), and slices are ordered
breadth-first (round 0 = all variants k in [0, SLICE), round 1 = next slice,
...).  search.py logs a summary line per completed slice, so a restart loses
at most one slice of work.  Breadth-first order also means the first hit
tends to have the smallest attainable k, i.e. the smallest N.

Run with --exec to run search.py in the foreground (for harness-tracked
background execution); default forks it detached.
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
SPECS = os.path.join(HERE, "specs_variants.json")
LOG = os.path.join(HERE, "search.log")
FOUND = os.path.join(HERE, "found.jsonl")
REMAINING = os.path.join(HERE, "remaining.json")

BLOCK = 32768
SLICE = 8 * BLOCK          # 262,144 k per work unit (~2 min on 4 cores)
KMAX = 1_500_000


def main():
    if os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
        print("hit already recorded in found.jsonl; not relaunching")
        return 1
    specs = json.load(open(SPECS))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    slices = []
    for k0 in range(0, KMAX, SLICE):
        for s in specs:
            name = f"{s['name']}@{k0}"
            if name in done:
                continue
            sl = dict(s)
            sl["name"] = name
            sl["kstart"] = k0
            sl["kmax"] = min(k0 + SLICE, KMAX)
            slices.append(sl)
    total = len(specs) * ((KMAX + SLICE - 1) // SLICE)
    print(f"{total} slices total, {len(done)} completed, "
          f"{len(slices)} remaining")
    if not slices:
        print("campaign budget exhausted with no hit")
        return 2
    json.dump(slices, open(REMAINING, "w"))
    argv = [sys.executable, os.path.join(GOLDBACH, "search.py"), REMAINING,
            "--procs", "4", "--out", FOUND]
    if "--exec" in sys.argv:
        with open(LOG, "a", buffering=1) as log:
            return subprocess.call(argv, cwd=GOLDBACH, stdout=log, stderr=log)
    with open(LOG, "a") as log:
        subprocess.Popen(argv, cwd=GOLDBACH, stdout=log, stderr=log,
                         start_new_session=True)
    print("relaunched search.py detached")
    return 0


if __name__ == "__main__":
    sys.exit(main())

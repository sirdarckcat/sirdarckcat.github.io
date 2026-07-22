"""Restart-safe driver for the E10 campaign, v3: foreground chunk mode.

Operational reality: the session container is reclaimed at every idle
moment, killing detached processes AND harness-tracked background tasks.
Compute only reliably advances while a session turn is actively executing
a foreground command.  So the campaign runs as timeboxed foreground
chunks: each invocation processes whole ~2-min slices one at a time until
the --chunk-seconds budget would be exceeded, then exits cleanly.

Slices are the 1,200 interleaved k-ranges of v2 (262,144 k per variant per
round, breadth-first across the 200 variants), checkpointed per slice in
search.log and resumed idempotently.

Exit codes: 0 = time budget used up (more work remains)
            2 = campaign budget exhausted, no hit
            3 = HIT recorded in found.jsonl -> stop and certify
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
SPECS = os.path.join(HERE, "specs_variants.json")
LOG = os.path.join(HERE, "search.log")
FOUND = os.path.join(HERE, "found.jsonl")
SLICE_JSON = os.path.join(HERE, "current_slice.json")

BLOCK = 32768
SLICE = 8 * BLOCK          # 262,144 k per work unit (~2.2 min on 4 cores)
KMAX = 1_500_000


def pending_slices():
    specs = json.load(open(SPECS))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    out = []
    for k0 in range(0, KMAX, SLICE):
        for s in specs:
            name = f"{s['name']}@{k0}"
            if name in done:
                continue
            sl = dict(s)
            sl["name"] = name
            sl["kstart"] = k0
            sl["kmax"] = min(k0 + SLICE, KMAX)
            out.append(sl)
    n_total = len(specs) * ((KMAX + SLICE - 1) // SLICE)
    return out, n_total, len(done)


def hit():
    return os.path.exists(FOUND) and os.path.getsize(FOUND) > 0


def main():
    budget = 540.0
    for i, a in enumerate(sys.argv):
        if a == "--chunk-seconds":
            budget = float(sys.argv[i + 1])
    t0 = time.time()
    if hit():
        print("HIT already recorded in found.jsonl")
        return 3
    slices, n_total, n_done = pending_slices()
    print(f"slices: {n_done}/{n_total} done, {len(slices)} pending; "
          f"chunk budget {budget:.0f}s", flush=True)
    if not slices:
        print("campaign budget exhausted with no hit")
        return 2
    slice_secs = 140.0     # running estimate of one slice's wall time
    ran = 0
    for sl in slices:
        if time.time() - t0 + slice_secs > budget:
            break
        json.dump([sl], open(SLICE_JSON, "w"))
        ts = time.time()
        with open(LOG, "a", buffering=1) as log:
            rc = subprocess.call(
                [sys.executable, os.path.join(GOLDBACH, "search.py"),
                 SLICE_JSON, "--procs", "4", "--out", FOUND],
                cwd=GOLDBACH, stdout=log, stderr=log)
        if rc != 0:
            print(f"search.py rc={rc} on {sl['name']}", flush=True)
            return rc
        slice_secs = 0.5 * slice_secs + 0.5 * (time.time() - ts)
        ran += 1
        if hit():
            print(f"HIT after slice {sl['name']} -> certify now")
            return 3
    print(f"chunk done: {ran} slices in {time.time()-t0:.0f}s "
          f"({n_done + ran}/{n_total} total)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

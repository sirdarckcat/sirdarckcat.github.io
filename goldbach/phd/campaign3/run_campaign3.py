"""Campaign 3 driver: budget game R(<200 digits) — beat g = 119,419.

Cover: ratchet session's round-2 leftover (Q=122,000, 88 classes, M=191d,
|U|=867, independently re-verified), 40 residue-swap variants, kmax=4.5e8
each, ceiling 199 digits. Any hit ⇒ g(N) ≥ 122,011 > 119,419 with N < 10^199.

Same restart-safe chunked design as campaign 2 (slice checkpoints in
search.log, batching for the sieve-inverse cache, --sort-tests), plus lazy
round materialization (only the earliest incomplete k-rounds are expanded)
and selective testing: --skip-frac 0.92 tests only the emptiest 8% of each
block, keeping ~30% of the hit mass at ~7x the raw scan rate (calibrated
2026-07-28: 15.0k k/s vs 1.8k k/s baseline, ~3x net discovery rate; the
sacrificed mass is accounted exactly and logged per-slice as hit%).

Exit codes: 0 time budget done, 2 budget exhausted, 3 HIT.
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
SPEC_FILES = ["specs_variants.json"]
LOG = os.path.join(HERE, "search.log")
FOUND = os.path.join(HERE, "found.jsonl")
SLICE_JSON = os.path.join(HERE, "current_slice.json")

BLOCK = 32768
SLICE = 32 * BLOCK             # 1,048,576 k per work unit (~50-60s)
KMAX = 450_000_000             # per variant; 199d ceiling caps at ~5.4e8
BATCH = 4
MAX_PENDING = 64               # lazy: expand at most this many pending slices


def pending_slices():
    specs = []
    for fn in SPEC_FILES:
        path = os.path.join(HERE, fn)
        if os.path.exists(path):
            specs.extend(json.load(open(path)))
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    out = []
    n_total = len(specs) * ((KMAX + SLICE - 1) // SLICE)
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
        if len(out) >= MAX_PENDING:
            break
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
    print(f"slices: {n_done}/{n_total} done; chunk budget {budget:.0f}s",
          flush=True)
    if not slices:
        print("campaign budget exhausted with no hit")
        return 2
    slice_secs = 65.0
    ran = 0
    i = 0
    while i < len(slices):
        room = int((budget - (time.time() - t0)) // slice_secs)
        if room < 1:
            break
        batch = slices[i:i + min(room, BATCH)]
        i += len(batch)
        json.dump(batch, open(SLICE_JSON, "w"))
        ts = time.time()
        with open(LOG, "a", buffering=1) as log:
            rc = subprocess.call(
                [sys.executable, os.path.join(GOLDBACH, "search.py"),
                 SLICE_JSON, "--procs", "4", "--sort-tests",
                 "--skip-frac", "0.92", "--p-est", "0.055",
                 "--sieve-b", "1000000", "--out", FOUND],
                cwd=GOLDBACH, stdout=log, stderr=log)
        if rc != 0:
            print(f"search.py rc={rc} on {batch[0]['name']}...", flush=True)
            return rc
        slice_secs = 0.5 * slice_secs + 0.5 * (time.time() - ts) / len(batch)
        ran += len(batch)
        if hit():
            print(f"HIT within batch ending {batch[-1]['name']} -> certify")
            return 3
    print(f"chunk done: {ran} slices in {time.time()-t0:.0f}s "
          f"({n_done + ran}/{n_total} total)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

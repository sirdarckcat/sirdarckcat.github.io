"""Campaign 2 driver: T(100,000) attack via the 168-digit blueprint (PR #20).

Same restart-safe chunked design as campaign 1 (v3), plus slice batching:
several slices are passed to one search.py process so the sieve-inverse
cache (variants share M) amortizes the per-spec init cost.

Target: N < 10^185 (strictly below the 186-digit incumbent t100k_r2,
g=109,357) with g(N) > 100,000.  Expected hit ~4.1e8 elements (E~19.84)
at ~176-digit N.

Exit codes: 0 = time budget used up, 2 = spec budget exhausted, 3 = HIT.
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
SPEC_FILES = ["specs_batch1.json"]      # extend with specs_reserve slices later
LOG = os.path.join(HERE, "search.log")
FOUND = os.path.join(HERE, "found.jsonl")
SLICE_JSON = os.path.join(HERE, "current_slice.json")

BLOCK = 32768
SLICE = 8 * BLOCK          # 262,144 k per work unit
KMAX = 1_500_000
BATCH = 4                  # slices per search.py process (cache amortization)


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
    slice_secs = 140.0
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
                 SLICE_JSON, "--procs", "4", "--out", FOUND],
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

#!/usr/bin/env python3
"""campaign3 on a GPU runtime: the variants in my_specs.json, k-major order, slices of 2^20 k as in
run_campaign3.py, each batch run by search_gpu.py with full hit mass (--skip-frac 0). Slices already
in search.log (this directory's, seeded with the committed campaign3 log lines of these variants)
are skipped. Stops on a hit (found.jsonl non-empty) or when the variants are exhausted.

    python3 run_c3gpu.py [--batch 8]
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = json.load(open(os.path.join(HERE, "my_specs.json")))
LOG, FOUND = os.path.join(HERE, "search.log"), os.path.join(HERE, "found.jsonl")
SLICE, KMAX = 1 << 20, 450_000_000
BATCH = int(sys.argv[sys.argv.index("--batch") + 1]) if "--batch" in sys.argv else 8


def done():
    d = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                d.add(m.group(1))
    return d


def pending(d):
    for k0 in range(0, KMAX, SLICE):
        for s in SPECS:
            name = f"{s['name']}@{k0}"
            if name not in d:
                yield dict(s, name=name, kstart=k0, kmax=min(k0 + SLICE, KMAX))


while True:
    if os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
        print("C3GPU-HIT: found.jsonl is not empty", flush=True)
        break
    batch = []
    for sl in pending(done()):
        batch.append(sl)
        if len(batch) >= BATCH:
            break
    if not batch:
        print("C3GPU-EXHAUSTED", flush=True)
        break
    json.dump(batch, open(os.path.join(HERE, "current_slices.json"), "w"))
    with open(LOG, "a", buffering=1) as log:
        rc = subprocess.call([sys.executable, os.path.join(HERE, "search_gpu.py"), os.path.join(HERE, "current_slices.json"),
                              "--goldbach", HERE, "--out", FOUND], cwd=HERE, stdout=log, stderr=log)
    if rc != 0:
        print(f"C3GPU-FAILED rc={rc} at {batch[0]['name']}", flush=True)
        break

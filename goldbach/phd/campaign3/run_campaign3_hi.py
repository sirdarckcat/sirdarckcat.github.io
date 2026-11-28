"""Campaign 3, CPU share at k >= 2^32: run_campaign3.py's chunked, restart-safe driver for the part of each vector's range
that the GPUs cannot scan (their kernels take k as u32), k in [2^32, kcap], kcap = (10^200 - N0) // M, so N < 10^200.

    python3 run_campaign3_hi.py SPECS.json [--chunk-seconds 3600] [--procs 4] [--batch 4]   (slices per engine call)

- Slices of 2^20 k as in run_campaign3.py, highest first (E falls as N grows), all vectors at one k0 before the next.
- Engine: sieve200/search_c.py next to search.py if it exists (the uarch session's drop-in: same arguments, log line
  and results), else search.py. Arguments: --sort-tests --skip-frac 0.92 --p-est 0.055 --sieve-b 1000000, as
  run_campaign3.py.
- Logs: search.log and found.jsonl next to this script, in run_campaign3.py's format. Merge by concatenation; the key
  <name>@<k0> is unique.

Exit codes: 0 chunk done, 2 all slices done, 3 HIT (found.jsonl not empty; already re-checked by verify_success).
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDBACH = os.path.dirname(os.path.dirname(HERE))
LOG, FOUND, SLICE_JSON = (os.path.join(HERE, f) for f in ("search.log", "found.jsonl", "current_slice.json"))
SLICE, KLO = 1 << 20, 1 << 32


def opt(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    specs = json.load(open(sys.argv[1]))
    for s in specs:
        for f in ("cover", "residual"):
            if isinstance(s.get(f), str):
                s[f] = json.loads(s[f])
        s["Q"] = int(s["Q"]); s["ceiling_digits"] = 200; s["stop_on_success"] = True
    budget, procs, BATCH = opt("--chunk-seconds", 3600.0), opt("--procs", 4), opt("--batch", 4)
    engine = os.path.join(GOLDBACH, "sieve200", "search_c.py")
    engine = engine if os.path.exists(engine) else os.path.join(GOLDBACH, "search.py")
    if os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
        print("HIT already recorded in found.jsonl"); return 3
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            m = re.match(r"\[(\S+)\] k=\[", line)
            if m:
                done.add(m.group(1))
    kcap = {s["name"]: (10 ** 200 - int(s["N0"])) // int(s["M"]) for s in specs}
    top = max(kcap.values()) // SLICE * SLICE
    pend = []
    for k0 in range(top, KLO - 1, -SLICE):
        for s in specs:
            name = f"{s['name']}@{k0}"
            if name in done or k0 > kcap[s["name"]]:
                continue
            pend.append(dict(s, name=name, kstart=k0, kmax=min(k0 + SLICE, kcap[s["name"]] + 1)))
        if len(pend) >= 256:
            break
    print(f"{os.path.basename(engine)}: {len(done)} slices done; chunk budget {budget:.0f}s", flush=True)
    if not pend:
        print("all slices done"); return 2
    t0, i = time.time(), 0
    while i < len(pend) and time.time() - t0 < budget:
        batch = pend[i:i + BATCH]; i += len(batch)
        json.dump(batch, open(SLICE_JSON, "w"))
        with open(LOG, "a", buffering=1) as log:
            rc = subprocess.call([sys.executable, engine, SLICE_JSON, "--procs", str(procs), "--sort-tests", "--skip-frac", "0.92",
                                  "--p-est", "0.055", "--sieve-b", "1000000", "--out", FOUND], cwd=GOLDBACH, stdout=log, stderr=log)
        if rc != 0:
            print(f"engine rc={rc} on {batch[0]['name']}", flush=True); return rc
        if os.path.exists(FOUND) and os.path.getsize(FOUND) > 0:
            print(f"HIT within batch ending {batch[-1]['name']} -> certify"); return 3
    print(f"chunk done: {i} slices in {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

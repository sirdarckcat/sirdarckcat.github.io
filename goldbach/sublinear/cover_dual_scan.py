#!/usr/bin/env python3
"""Scan the members of many covers for a number below 10^digits with g(N) >= Q (the fixed-gap game), one cover after another.

    python3 cover_dual_scan.py covers.txt Q digits workdir search_c.py [procs=4] [sieve_b=10000000] [skip_frac=0.997] [p_est=0.042] [max_covers=0]

covers.txt holds lines "COVER k r:a r:a ..." (ptcover's PT_DUMP) or "BEST r:a ..."; the covers are taken in order of the rows
they leave, fewest first.  Each is turned into a spec (cover_dual_spec.py) and given to the uarch session's search_c.py
(goldbach/sieve200 on its branch: C sieve, the emptiest members tested with base-2 Fermat tests, a member that survives
is verified by search.py).  workdir/done.txt lists the covers finished, so a rerun resumes; workdir/log.txt has one line
per cover; the scan stops at the first hit with fewer than digits + 1 digits (workdir/found.jsonl).
"""
import sys, os, json, subprocess, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__))
covers_file, Q, digits, work, search_c = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
procs = sys.argv[6] if len(sys.argv) > 6 else "4"; sieve_b = sys.argv[7] if len(sys.argv) > 7 else "10000000"
skip = sys.argv[8] if len(sys.argv) > 8 else "0.997"; p_est = sys.argv[9] if len(sys.argv) > 9 else "0.042"
max_covers = int(sys.argv[10]) if len(sys.argv) > 10 else 0
os.makedirs(work, exist_ok=True)
covers = {}
for l in open(covers_file):
    t = l.split()
    if not t or t[0] not in ("COVER", "BEST"): continue
    cls = " ".join(u for u in t[1:] if ":" in u); k = int(t[1]) if t[0] == "COVER" else -1
    covers[hashlib.sha1(cls.encode()).hexdigest()[:12]] = (k, cls)
order = sorted(covers.items(), key=lambda kv: (kv[1][0], kv[0]))
if max_covers: order = order[:max_covers]
done = set(l.split()[0] for l in open(os.path.join(work, "done.txt"))) if os.path.exists(os.path.join(work, "done.txt")) else set()
found = os.path.join(work, "found.jsonl")
print(f"{len(order)} covers, {len(done)} done; rows from {order[0][1][0]} to {order[-1][1][0]}", flush=True)
env = dict(os.environ, SEARCH_C_CHUNK=os.environ.get("SEARCH_C_CHUNK", "32"))
for h, (k, cls) in order:
    if h in done: continue
    cf = os.path.join(work, "cover.txt"); sf = os.path.join(work, "spec.json")
    open(cf, "w").write("BEST " + cls + "\n")
    r = subprocess.run([sys.executable, os.path.join(HERE, "cover_dual_spec.py"), cf, str(Q), str(digits), f"d{digits}_{h}", sf], capture_output=True, text=True)
    if r.returncode: print("spec failed:", r.stderr, flush=True); sys.exit(1)
    t0 = time.time()
    r = subprocess.run([sys.executable, search_c, sf, "--procs", procs, "--sort-tests", "--skip-frac", skip, "--p-est", p_est, "--sieve-b", sieve_b, "--out", found],
                       capture_output=True, text=True, env=env)
    line = [l for l in r.stdout.splitlines() if l.startswith("[")]
    with open(os.path.join(work, "log.txt"), "a") as f: f.write(f"{h} rows={k} {line[-1] if line else 'NO LINE ' + r.stderr[-300:]}\n")
    with open(os.path.join(work, "done.txt"), "a") as f: f.write(f"{h} {k} {time.time() - t0:.0f}\n")
    if os.path.exists(found):
        hits = [json.loads(l) for l in open(found) if l.strip()]
        good = [x for x in hits if x["digits"] <= digits and x["g"] >= Q]
        if good:
            print("HIT", json.dumps(good[0]), flush=True)
            open(os.path.join(work, "hit_cover.txt"), "w").write("BEST " + cls + "\n")
            break

#!/usr/bin/env python3
"""(As run on 22 Nov, with the container's absolute path to proth/ made relative.)

Fallback pool for the 16M rung: sieve t in [0, T) to B with desert.sieve_candidates,
exactly as the main pool (survivors_T32768_B1000000000.json) was made, then keep t >= T0.

    python3 ext_sieve.py spec.json T0 T B procs out.json [main_pool.json]

If main_pool.json is given, the survivors below T0 must equal it (a free check that this
run reproduces the main pool's sieve).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))  # proth/
import desert  # noqa: E402

spec_path, T0, T, B, procs, out = sys.argv[1:7]
T0, T, B, procs = int(T0), int(T), int(float(B)), int(procs)
spec = json.load(open(spec_path))
assert T < (1 << spec["tbits"])
t_start = time.time()
alive = [int(t) for t in desert.sieve_candidates(spec, T, B, procs)]
if len(sys.argv) > 7:
    main_pool = json.load(open(sys.argv[7]))
    low = [t for t in alive if t < T0]
    print(f"check: {len(low)} survivors below {T0} here, {len(main_pool)} in the main pool, "
          f"identical={low == sorted(int(t) for t in main_pool)}", flush=True)
    if low != sorted(int(t) for t in main_pool):
        sys.exit("MISMATCH with the main pool")
surv = [t for t in alive if t >= T0]
with open(out + ".tmp", "w") as fh:
    json.dump(surv, fh)
os.replace(out + ".tmp", out)
print(f"DONE: {len(surv)} survivors in [{T0}, {T}) after primes < {B:.3g}, "
      f"{time.time() - t_start:.0f}s", flush=True)

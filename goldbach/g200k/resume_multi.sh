#!/bin/bash
# Restart many-cover workers detached (setsid nohup: they outlive the shell that started them), skipping every spec whose
# summary line is already in the worker's log.  Appends to the same logs and found files as run_multi.sh.
#   SKIP=0.992 PEST=0.0417 ./resume_multi.sh PREFIX "0 1"
D="$(cd "$(dirname "$0")" && pwd)"
P=${1:?prefix}; WS=${2:-"0 1 2 3"}
for w in $WS; do
  python3 - "$P" "$w" <<'PY'
import json, re, sys, os
P, w = sys.argv[1], sys.argv[2]
done = set()
if os.path.exists(f"{P}_w{w}.log"):
    for l in open(f"{P}_w{w}.log"):
        m = re.match(r"\[(\S+)\] k=\[", l)
        if m: done.add(m.group(1))
specs = [s for s in json.load(open(f"{P}_w{w}.json")) if s["name"] not in done]
json.dump(specs, open(f"{P}_r_w{w}.json", "w"))
print(f"worker {w}: {len(done)} specs done, {len(specs)} left")
PY
  SEARCH_C_FERMAT=fmw SEARCH_C_CHUNK=${CHUNK:-64} setsid nohup python3 "$D/../sieve200/search_c.py" "${P}_r_w$w.json" --procs 1 --sort-tests \
    --skip-frac ${SKIP:-0.992} --p-est ${PEST:-0.042} --sieve-b ${SIEVE_B:-10000000} --kmax 1 --out "${P}_found_w$w.jsonl" >> "${P}_w$w.log" 2>&1 < /dev/null &
done
sleep 1

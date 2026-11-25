#!/bin/bash
# Many-cover scan: one search_c.py --procs 1 per worker file (cover_specs.py's PREFIX_w<i>.json), each its own log and found file.
#   SKIP=0.992 PEST=0.042 ./run_multi.sh PREFIX NWORKERS
D="$(cd "$(dirname "$0")" && pwd)"
P=${1:?prefix}; W=${2:-4}
for ((w = 0; w < W; w++)); do
  SEARCH_C_FERMAT=fmw SEARCH_C_CHUNK=${CHUNK:-64} python3 "$D/../sieve200/search_c.py" "${P}_w$w.json" --procs 1 --sort-tests \
    --skip-frac ${SKIP:-0.992} --p-est ${PEST:-0.042} --sieve-b ${SIEVE_B:-10000000} --kmax 1 --out "${P}_found_w$w.jsonl" > "${P}_w$w.log" 2>&1 &
done
wait

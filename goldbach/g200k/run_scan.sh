#!/bin/bash
# g >= 200,000 scan of a slices file (slices.py): fmw Fermat (../fermatw), B = 10^7, the emptiest 1 - SKIP of each block tested.
#   PROCS=3 SKIP=0.975 OUT=found.jsonl ./run_scan.sh slices.json
D="$(cd "$(dirname "$0")" && pwd)"
SEARCH_C_FERMAT=fmw SEARCH_C_CHUNK=${CHUNK:-16} python3 "$D/../sieve200/search_c.py" "${1:?slices.json}" \
  --procs ${PROCS:-3} --sort-tests --skip-frac ${SKIP:-0.975} --p-est ${PEST:-0.031} --sieve-b ${SIEVE_B:-10000000} --kmax 1 --out "${OUT:-found.jsonl}"

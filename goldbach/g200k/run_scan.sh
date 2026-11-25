#!/bin/bash
# 400-digit g >= 200,000 scan: cover400_k1010 (159 moduli to 941, 1010 rows), slices of 3,145,728 members, fmw Fermat (L = 26)
cd "$(dirname "$0")"
SEARCH_C_FERMAT=fmw SEARCH_C_CHUNK=16 python3 /home/user/sirdarckcat.github.io/goldbach/sieve200/search_c.py ${1:?slices.json} \
  --procs ${PROCS:-3} --sort-tests --skip-frac ${SKIP:-0.975} --p-est 0.031 --sieve-b 10000000 --kmax 1 --out ${OUT:-found.jsonl}

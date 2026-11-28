#!/bin/bash
# (As run on 22 Nov, with absolute paths made relative to this directory.)
# Fallback pool for the 16M rung, on this container's otherwise idle cores: t in [32768, 131072)
# sieved by primes < 1e9 (desert.py), then [1e9, 1e11) and [1e11, 3e11) (deepsieve), the same
# chain as the main pool. Used only if t < 32768 holds no prime (~13% after 5,517 misses).
E=$(cd "$(dirname "$0")" && pwd)          # this directory (was a scratch directory when run)
PR=$(cd "$E/../../.." && pwd)               # goldbach/proth
RQ=$PR/runs/q16045849
cd $E
say() { echo "$(date -u +%FT%TZ) $*" >> chain.log; }
say "start"
nice -n 10 python3 ext_sieve.py $RQ/spec.json 32768 131072 1e9 4 survivors_T131072_B1000000000.json \
    $RQ/survivors_T32768_B1000000000.json > sieve_1e9.log 2>&1 || { say "EXT-FAILED sieve_1e9"; exit 1; }
say "$(tail -1 sieve_1e9.log)"
nice -n 10 python3 $PR/deep_sieve.py $RQ/spec.json survivors_T131072_B1000000000.json 1e9 1e11 \
    survivors_T131072_B100000000000.json --threads 4 --bin $E/deepsieve --every 600 > ds_1e9_1e11.log 2>&1 \
    || { say "EXT-FAILED ds_1e9_1e11"; exit 1; }
say "$(tail -1 ds_1e9_1e11.log)"
nice -n 10 python3 $PR/deep_sieve.py $RQ/spec.json survivors_T131072_B100000000000.json 1e11 3e11 \
    survivors_T131072_B300000000000.json --threads 4 --bin $E/deepsieve --every 600 > ds_1e11_3e11.log 2>&1 \
    || { say "EXT-FAILED ds_1e11_3e11"; exit 1; }
say "$(tail -1 ds_1e11_3e11.log)"
say "EXT-DONE"

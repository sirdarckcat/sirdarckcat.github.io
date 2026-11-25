#!/bin/bash
# Idle-core CPU scan at 200 digits (the lead's ruling of 19:52Z, relayed by Research at 20:04Z): the first 88 odd primes with 479.
# Workers 0, 1, 2: target 160,367 (the record) on slices 0, 1, 2 of the first 3,000 covers (interleaved by index).
# Worker 3's slice at target 120,000 (a calibration run: many events, for the accounting of this pipeline and for the overshoot law).
cd /home/user/scan479
export SEARCH_C_FERMAT=fm13
export SEARCH_C_CHUNK=128
for w in 0 1 2; do
  nohup nice -n 10 python3 code/goldbach/sieve200/search_c.py f479_w$w.json --procs 1 --sort-tests --skip-frac 0.985 --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out f479_found_w$w.jsonl > f479_w$w.log 2>&1 &
done
nohup nice -n 10 python3 code/goldbach/sieve200/search_c.py f479lo_w3.json --procs 1 --sort-tests --skip-frac 0.985 --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out f479lo_found_w3.jsonl > f479lo_w3.log 2>&1 &
sleep 1
echo started

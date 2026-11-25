#!/bin/bash
# Calibration worker: slice 3 of the first 3,000 covers at target 80,000 (E^ about 15), for the accounting of this pipeline and the overshoot law at 200 digits.
cd /home/user/scan479
export SEARCH_C_FERMAT=fm13
export SEARCH_C_CHUNK=128
nohup nice -n 10 python3 code/goldbach/sieve200/search_c.py f479t80000_w3.json --procs 1 --sort-tests --skip-frac 0.985 --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out f479t80000_found_w3.jsonl > f479t80000_w3.log 2>&1 &
sleep 1
echo started

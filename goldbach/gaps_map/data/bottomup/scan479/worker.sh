#!/bin/bash
# usage: worker.sh TAG W   (TAG = f479 for the record target, f479t80000 for the calibration target)
# Resumes after a restart of the container: skips the covers whose summary line is already in the log, appends to the log, writes finds to a new file.
cd /home/user/scan479
TAG=$1
W=$2
export SEARCH_C_FERMAT=fm13
export SEARCH_C_CHUNK=128
N=$(grep -c '^\[c' ${TAG}_w${W}.log 2>/dev/null)
N=${N:-0}
python3 -c "
import json, sys
s = json.load(open('${TAG}_w${W}.json'))
json.dump(s[${N}:], open('${TAG}_w${W}_r.json', 'w'))
print('worker ${TAG} ${W}: resume from cover ${N} of', len(s), flush=True)
"
exec nice -n 10 python3 code/goldbach/sieve200/search_c.py ${TAG}_w${W}_r.json --procs 1 --sort-tests --skip-frac 0.985 --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out ${TAG}_found_w${W}_$(date +%s).jsonl >> ${TAG}_w${W}.log 2>&1

#!/bin/bash
# CPU share of Q = 150,000 at k >= 2^32 on this GPU host: the uarch session's search_c.py (C sieve + IFMA Fermat tests) under
# run_campaign3_hi.py, 44 processes, niced below the GPU campaign. Checks first (test_dropin.py, test_fm13.py).
mkdir -p /content/c150cpu && cd /content/c150cpu && tar -xzf /content/cpuq150_tree.tgz
cp /content/cpuq150_specs.json /content/c150cpu/goldbach/phd/campaign3_hi/specs.json
D=/content/c150cpu/goldbach/phd/campaign3_hi
echo "$(date -u +%FT%TZ) cpu flags: $(grep -o -w 'avx512ifma\|avx512f' /proc/cpuinfo | sort -u | tr '\n' ' ')" >> $D/driver.log
cd /content/c150cpu/goldbach/sieve200 && timeout 900 python3 test_dropin.py > /content/c150cpu/dropin.out 2>&1
cd /content/c150cpu/goldbach/fermat661 && timeout 900 python3 test_fm13.py > /content/c150cpu/fm13.out 2>&1
echo "$(date -u +%FT%TZ) tests: $(tail -n 1 /content/c150cpu/dropin.out) / $(tail -n 1 /content/c150cpu/fm13.out)" >> $D/driver.log
grep -q "ALL IDENTICAL" /content/c150cpu/dropin.out && grep -q "ALL OK" /content/c150cpu/fm13.out || { echo "C3CPU-END rc=99 tests failed" >> $D/driver.log; exit 1; }
cd $D
while true; do
  nice -n 5 python3 run_campaign3_hi.py specs.json --chunk-seconds 3600 --procs 44 >> driver.log 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) run_campaign3_hi rc=$rc" >> driver.log
  [ $rc -ne 0 ] && break
done
echo "C3CPU-END rc=$rc" >> driver.log

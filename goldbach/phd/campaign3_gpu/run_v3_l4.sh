#!/bin/bash
# The L4: check search_gpu3.py on this GPU (check_v3.py), then its campaign mode as on the G4.
cd /content/c3g
python3 check_v3.py specs_variants.json selftest_q3001.json /content/c3g > v3check.out 2>&1
if ! grep -q "ALL V3 CHECKS PASSED" v3check.out; then echo "C3GPU-END rc=99 v3 checks failed on this GPU $(date -u +%FT%TZ)" >> driver.log; exit 1; fi
echo "$(date -u +%FT%TZ) v3 checks passed; start search_gpu3 campaign" >> driver.log
python3 search_gpu3.py --campaign /content/c3g --goldbach /content/c3g --batch 32 --pool 1048576 \
  --skip-frac 0.97 --p-est 0.055 --kmax 543859952 --klo 272629760 --desc >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

#!/bin/bash
# campaign3, search_gpu5.py (GPU sieve + GPU tests) in DIR, N < 10^200, k in [KLO, KMAX) top first, --no-stop.
#   KERNEL (28 on RTX PRO 6000, 3 elsewhere), SKIPF (skip fraction), KLO, KMAX from the environment.   bash run_v5_campQ.sh DIR
D=$1
cd $D
echo "$(date -u +%FT%TZ) start search_gpu5 campaign (GPU sieve) in $D, f=${SKIPF:-0.97} kernel ${KERNEL:-3}, $(python3 -c 'import json; s=json.load(open("my_specs.json")); print(len(s), "variants, Q =", s[0]["Q"])')" >> driver.log
python3 /content/c3g/search_gpu5.py --campaign $D --goldbach /content/c3g --batch ${BATCH:-32} --pool ${POOL:-1048576} \
  --skip-frac ${SKIPF:-0.97} --p-est 0.055 --kmax ${KMAX:-4294967296} --klo ${KLO:-1073741824} --desc --no-stop --kernel ${KERNEL:-3} --sieve200 ${SIEVE200:-/content/gs/goldbach/sieve200} --sieve-threads ${SIEVE_THREADS:-256} >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

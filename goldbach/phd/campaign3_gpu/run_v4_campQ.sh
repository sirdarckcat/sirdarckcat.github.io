#!/bin/bash
# campaign3 v3 on a cover family in DIR (its own my_specs.json and search.log), N < 10^200: k in [2^30, 2^32)
# (the kernel takes k as u32), top first, skip-frac 0.97, --no-stop.   bash run_v3_campQ.sh DIR
D=$1
cd $D
echo "$(date -u +%FT%TZ) start search_gpu4 campaign (CPU feeder) in $D, $(python3 -c 'import json; s=json.load(open("my_specs.json")); print(len(s), "variants, Q =", s[0]["Q"])')" >> driver.log
python3 /content/c3g/search_gpu4.py --campaign $D --threads ${THREADS:-46} --goldbach /content/c3g --batch 32 --pool 1048576 \
  --skip-frac 0.97 --p-est 0.055 --kmax ${KMAX:-4294967296} --klo ${KLO:-1073741824} --desc --no-stop --kernel ${KERNEL:-3} >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

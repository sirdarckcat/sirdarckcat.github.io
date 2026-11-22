#!/bin/bash
# campaign3 v3, campaign mode with --no-stop (keep going after hits): bash run_v3_camp.sh DIR
D=$1
cd $D
echo "$(date -u +%FT%TZ) (re)start search_gpu3 campaign --no-stop, $(python3 -c 'import json; print(len(json.load(open("my_specs.json"))))') variants" >> driver.log
python3 /content/c3g/search_gpu3.py --campaign $D --goldbach /content/c3g --batch 32 --pool 1048576 \
  --skip-frac 0.97 --p-est 0.055 --kmax 543859952 --klo 272629760 --desc --no-stop >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

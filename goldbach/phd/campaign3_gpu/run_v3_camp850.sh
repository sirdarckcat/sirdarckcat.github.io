#!/bin/bash
# campaign3 v3 on the 850-row cover's variants, N < 10^200: k in [2^31, 2^32) (the kernel takes k as u32), top first,
# skip-frac 0.97, --no-stop. Directory /content/c850 (its own my_specs.json and search.log).
D=/content/c850
cd $D
echo "$(date -u +%FT%TZ) start search_gpu3 campaign (850-row cover, N < 10^200), $(python3 -c 'import json; print(len(json.load(open("my_specs.json"))))') variants" >> driver.log
python3 /content/c3g/search_gpu3.py --campaign $D --goldbach /content/c3g --batch 32 --pool 1048576 \
  --skip-frac 0.97 --p-est 0.055 --kmax 4294967296 --klo 2147483648 --desc --no-stop >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

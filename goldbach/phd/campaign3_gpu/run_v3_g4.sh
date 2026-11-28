#!/bin/bash
# campaign3 v3 on this GPU (G4): search_gpu3.py campaign mode, the top half of k first, skip-frac 0.97.
cd /content/c3g_g4
echo "$(date -u +%FT%TZ) start search_gpu3 campaign" >> driver.log
python3 /content/c3g/search_gpu3.py --campaign /content/c3g_g4 --goldbach /content/c3g --batch 32 --pool 1048576 \
  --skip-frac 0.97 --p-est 0.055 --kmax 543859952 --klo 272629760 --desc >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

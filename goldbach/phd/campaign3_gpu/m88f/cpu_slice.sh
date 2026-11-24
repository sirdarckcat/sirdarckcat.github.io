#!/bin/bash
# The CPU engine (sieve200/search_c.py, the CPU shares' tree) on the m88f slice of m88f_l4.sh (q170000_m88f_t1_v1, k in [2^32 - 2^20, 2^32)) at f = 0.97 and 0.9, with the GPU normal path's
# parameters (B = 10^6, block 32768, p-est 0.055): its slice lines must equal search_gpu5.py's.
W=/content/m88f_cpu; mkdir -p $W; cd $W; rm -f out_*.txt found_*.jsonl result.txt
G=/content/c150cpu/goldbach
for f in 0.97 0.9; do
  timeout 3000 python3 $G/sieve200/search_c.py /content/slice_m88f.json --procs 8 --block 32768 --sieve-b 1000000 --skip-frac $f --p-est 0.055 --out $W/found_$f.jsonl > $W/out_$f.txt 2>&1
  echo "rc=$?" >> $W/out_$f.txt
done
grep -h "^\[" $W/out_*.txt > result.txt; echo CPUSLICE-DONE >> result.txt

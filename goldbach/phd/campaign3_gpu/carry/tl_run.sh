#!/bin/bash
# The lead's item 1, step 1 (25 Nov): uarch's time_launch.py on this RTX PRO 6000, production paused (always resumed): the production 29-bit step (s29_asm)
# and the 28-bit s1r_asm, launches of 8 .. 2^21 tests, with this card's own gpu_fermat28.py and step files (/content/f29fr).
W=/content/tl; rm -rf $W; mkdir -p $W
cp /content/f29fr/*.py /content/f29fr/*.cuh $W/ 2>/dev/null; cp /content/tl_time_launch.py $W/time_launch.py; cp /content/tl_bench_persist.py $W/bench_persist.py
P=$(pgrep -f "search_gpu5[.]py --campaign /content/c170r " | head -n 1)
[ -n "$P" ] || { echo "TL: no production process" > $W/tl.log; exit 1; }
trap 'kill -CONT $P 2>/dev/null' EXIT
echo "TL paused $P $(date -u +%T)" > $W/tl.log; kill -STOP $P; sleep 3
cd $W
for v in s29_asm s1r_asm; do timeout 300 python3 time_launch.py --variant $v > tl_$v.txt 2>&1; echo "TL $v rc=$? $(date -u +%T)" >> tl.log; done
kill -CONT $P; trap - EXIT; echo "TL resumed $P $(date -u +%T)" >> tl.log; echo TL-DONE >> tl.log

#!/bin/bash
# calibration ladder, cheap rungs first; one calib.py per rung, 2 processes, disjoint k ranges per cover
cd /tmp/claude-0/-home-user-sirdarckcat-github-io/b6b07341-7caa-5bed-9677-bea302b80c6e/scratchpad/calib
C=/home/user/sirdarckcat.github.io/goldbach/g200k/calib.py
D100=cover_d100_Q75000_49primes_k709.txt
D150=cover_d150_Q123000_69primes_k1003.txt
M=1048576
python3 $C $D100 25000 0                $((48*M))   0.98 10000000 r100_25k.json --procs 2
python3 $C $D150 40000 0                $((24*M))   0.98 10000000 r150_40k.json --procs 2
python3 $C $D100 30000 $((48*M))        $((128*M))  0.98 10000000 r100_30k.json --procs 2
python3 $C $D150 50000 $((24*M))        $((160*M))  0.98 10000000 r150_50k.json --procs 2
python3 $C $D100 35000 $((176*M))       $((560*M))  0.98 10000000 r100_35k.json --procs 2
python3 $C $D150 60000 $((184*M))       $((1024*M)) 0.98 10000000 r150_60k.json --procs 2
echo LADDER1 DONE

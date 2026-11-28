#!/bin/bash
# calibration ladder, expensive rungs (k ranges after ladder1's: 100 digits from 736M, 150 digits from 1208M)
cd /tmp/claude-0/-home-user-sirdarckcat-github-io/b6b07341-7caa-5bed-9677-bea302b80c6e/scratchpad/calib
C=/home/user/sirdarckcat.github.io/goldbach/g200k/calib.py
D100=cover_d100_Q75000_49primes_k709.txt
D150=cover_d150_Q123000_69primes_k1003.txt
M=1048576
python3 $C $D100 40000 $((736*M))         $((1536*M)) 0.98 10000000 r100_40k.json --procs 2
python3 $C $D150 70000 $((1208*M))        $((3584*M)) 0.98 10000000 r150_70k.json --procs 2
python3 $C $D100 45000 $((2272*M))        $((4096*M)) 0.98 10000000 r100_45k.json --procs 2
echo LADDER2 DONE

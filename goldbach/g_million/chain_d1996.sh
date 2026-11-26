#!/bin/bash
# T5 (c): the 2,000-digit scan on hb4657_rs1 (629 moduli, 2,825 rows): sieve pass 1 for 4e7 members against the primes in
# (4657, 1e9], then the 15,000 emptiest members (pass 2 and tests, until the first hit). A copy of run/chain_d1996.sh.
cd /home/user/sirdarckcat.github.io/goldbach/g_million
[ -f run/counts_d1996.u16 ] || OMP_NUM_THREADS=4 ./sieve setup_d1996.bin 4657 1000000000 40000000 run/counts_d1996.u16.part 2> run/sieve1_d1996.log && mv run/counts_d1996.u16.part run/counts_d1996.u16
[ -f run/counts_d1996.u16 ] || { echo "pass 1 output missing"; exit 1; }
python3 run_scan.py d1996 4657 1000000000 40000000 15000

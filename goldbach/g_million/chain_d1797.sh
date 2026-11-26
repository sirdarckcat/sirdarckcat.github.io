#!/bin/bash
# T5: the 1,797-digit scan on hb4201_b2 (574 moduli, 3,103 rows): sieve pass 1 for 6e7 members against the primes in (4201, 1e9],
# then the 100,000 emptiest members (pass 2, then tests with the uarch session's IFMA kernel, until the first hit).
cd /home/user/sirdarckcat.github.io/goldbach/g_million
[ -f run/counts_d1797.u16 ] || { OMP_NUM_THREADS=4 ./sieve setup_d1797.bin 4201 1000000000 60000000 run/counts_d1797.u16.part 2> run/sieve1_d1797.log && mv run/counts_d1797.u16.part run/counts_d1797.u16; }
[ -f run/counts_d1797.u16 ] || { echo "pass 1 output missing"; exit 1; }
T5_TESTER=test_members_fmw.py python3 run_scan.py d1797 4201 1000000000 60000000 100000

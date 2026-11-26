#!/bin/bash
# T5, the next step of the descent (research, 25 Nov 19:22 UTC, lowest priority: nice 19, dropped the moment a 200-digit piece
# arrives): about 1,700 digits with g(N) >= 10^6, on 547 moduli (the odd primes up to 3,947).
#   1. four 20k-sweep heat-bath anneals from hb4201_b2 restricted to the moduli up to 3,947 (run/restr3947.txt), the best kept;
#   2. members.py: setup_d1700.bin / .json;
#   3. sieve pass 1 for 1e8 members against the primes in (3947, 1e9];
#   4. run_scan.py: the 300,000 emptiest members, pass 2, then tests with the uarch session's IFMA kernel until the first hit.
# Every step is resumable: rerun the script and it skips what is done.
cd /home/user/sirdarckcat.github.io/goldbach/g_million
set -e
Q=1000003
if [ ! -f hb3947.txt ]; then
  cd run
  for s in 1 2 3 4; do
    if [ ! -f x3947_s$s.txt ]; then
      ( ../heatbath2 $Q restr3947.txt 20000 1.8 10.0 $s x3947_s$s.txt.part 2> x3947_s$s.log && mv x3947_s$s.txt.part x3947_s$s.txt ) &
    fi
  done
  wait
  cd ..
  for s in 1 2 3 4; do [ -f run/x3947_s$s.txt ] || { echo "anneal $s failed"; exit 1; }; done
  best=$(for s in 1 2 3 4; do echo "$(head -1 run/x3947_s$s.txt | sed 's/.*rows in no class: \([0-9]*\).*/\1/') run/x3947_s$s.txt"; done | sort -n | head -1)
  echo "anneals: $(for s in 1 2 3 4; do head -1 run/x3947_s$s.txt | sed 's/.*rows in no class: \([0-9]*\).*/\1/'; done | tr '\n' ' '); best: $best"
  cp "${best#* }" hb3947.txt
fi
[ -f setup_d1700.bin ] || python3 members.py hb3947.txt d1700
[ -f run/counts_d1700.u16 ] || { OMP_NUM_THREADS=4 ./sieve setup_d1700.bin 3947 1000000000 100000000 run/counts_d1700.u16.part 2> run/sieve1_d1700.log && mv run/counts_d1700.u16.part run/counts_d1700.u16; }
T5_TESTER=test_members_fmw.py python3 run_scan.py d1700 3947 1000000000 100000000 300000

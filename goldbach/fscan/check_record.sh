#!/bin/bash
# check_record.sh [fscan binary]
# Scans exactly one member, N = 83668534093338795647672 (g(N) = 10,159: vector N0 = 10397114829367892,
# k = 6395326, 197 residual primes) with the production thresholds of class 197 and checks that the scanner
# reports it.  It exercises the score, the exact stage and every Fermat test of the 111 rows left after the
# primes <= 383 (all must be composite) in one second.   Build first:  gcc -O3 -march=native -fopenmp -o fscan fscan.c -lm
BIN=${1:-./fscan}
N=83668534093338795647672
NM1=83668534093338795647671          # N - 1, as text: bash arithmetic is 64-bit
N0=10397114829367892
OUT=$($BIN 10007 383 197 197 $NM1 $N 102 113 rref=197 one=$N0 threads=1 2>&1)
echo "$OUT" | grep -E '^S |^STATS' | sed 's/STATS Q=.*| vectors/STATS vectors/' | cut -c1-110
if echo "$OUT" | grep -q "^S $N 6395326 $N0 197\$" && echo "$OUT" | grep -q "tests=111 prps=0 found=1"; then echo "OK: the record member is reported, 111 rows proved composite"; else echo "FAIL"; exit 1; fi

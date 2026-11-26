#!/bin/bash
# The runs of the README. Writes the full outputs to out/ (60 MB) and the family outputs to sym/.
# usage: ./run_all.sh [PYTHON]      (PYTHON needs python-flint, for the family only)
set -e
cd "$(dirname "$0")"
PY=${1:-python3}
gcc -O2 -march=native -o w3 w3.c
mkdir -p out sym
run() { ./w3 "$@"; }
# F_3, leading coefficient 1 and -1 (mu = 2)
for mu in 1 2; do
  [ $mu = 1 ] && { run 3 9 1 9 out/q3n9_mu1.txt 4 5 7 8 10 20 -l 3; run 3 10 1 9 out/q3n10_mu1.txt 4 7 8 10 20 50 -l 5; run 3 11 1 9 out/q3n11_mu1.txt 5 7 8 10 20 50 -l 6; }
  run 3 12 $mu 9 out/q3n12_mu$mu.txt 7 8 10 20 50 120 -l 6
  run 3 13 $mu 9 out/q3n13_mu$mu.txt 7 8 10 20 50 120 -l 6 7
  run 3 14 $mu 9 out/q3n14_mu$mu.txt 8 10 20 50 120 -l 7
  run 3 15 $mu 9 out/q3n15_mu$mu.txt 8 10 20 50 120 -l 7
  run 3 16 $mu 9 out/q3n16_mu$mu.txt 10 20 50 120 -l 7 8
  run 3 17 $mu 9 out/q3n17_mu$mu.txt 7 10 20 50 120 -l 8
  run 3 18 $mu 9 out/q3n18_mu$mu.txt 7 10 20 50 120 -l 8
done
# F_5 (non-square 2), F_7 (non-square 3), F_9 (non-square 1 + i, label 4)
for mu in 1 2; do
  run 5 7 $mu 6 out/q5n7_mu$mu.txt 6 7 8 10 -l 5
  run 5 8 $mu 6 out/q5n8_mu$mu.txt 7 8 10 25 -l 5 6
  run 5 9 $mu 6 out/q5n9_mu$mu.txt 7 8 10 25 -l 6
  run 5 10 $mu 6 out/q5n10_mu$mu.txt 8 10 25 100 -l 6 7
  run 5 11 $mu 6 out/q5n11_mu$mu.txt 6 8 10 25 100 -l 7
done
run 5 12 1 6 out/q5n12_mu1.txt 6 10 25 100 400 -l 7 8
for mu in 1 3; do
  run 7 6 $mu 5 out/q7n6_mu$mu.txt 6 8 9 12 -l 5
  run 7 7 $mu 5 out/q7n7_mu$mu.txt 6 8 9 12 -l 5
  run 7 8 $mu 5 out/q7n8_mu$mu.txt 5 6 8 9 12 18 60 -l 7
  run 7 9 $mu 5 out/q7n9_mu$mu.txt 5 6 8 9 12 18 60 -l 7
done
run 7 10 1 5 out/q7n10_mu1.txt 5 6 9 12 18 60 200 -l 7 8
for mu in 1 4; do
  run 9 5 $mu 5 out/q9n5_mu$mu.txt 2 4 -l 3
  run 9 6 $mu 5 out/q9n6_mu$mu.txt 3 5 6 7 8 12 20 -l 4
  run 9 7 $mu 5 out/q9n7_mu$mu.txt 4 6 7 8 12 20 -l 5 6
  run 9 8 $mu 5 out/q9n8_mu$mu.txt 4 5 8 12 20 100 -l 6 7
  run 9 9 $mu 5 out/q9n9_mu$mu.txt 4 5 6 12 20 100 -l 7 8
done
# the translation-invariant family
for job in "3 9 8 3" "3 12 8 3" "3 15 8 3" "3 18 9 3" "3 21 9 3" "3 24 9 3" "3 27 10 3" "3 30 10 3" "3 33 10 3" \
           "5 10 5 1" "5 15 6 1" "5 20 6 1" "5 25 6 1" "7 7 5 0" "7 14 5 0" "7 21 5 0"; do
  set -- $job
  $PY -I symfam.py $1 $2 $3 $4 > sym/q$1n$2.txt
done
python3 tables.py out sym > tables.md

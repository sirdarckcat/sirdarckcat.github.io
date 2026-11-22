#!/bin/bash
# run_classes.sh Xmax R1 R2 ... : one fscan pass per residual class, resumable (runs/Rxxx.done), output appended to runs/Rxxx.log
# thresholds: theta = 99 at R = 194, plus one per class; Ta = 113; score primes up to 383.
X=$1; shift
cd "$(dirname "$0")"
for R in "$@"; do
  TH=$((99 + R - 194))
  ./fscan 10007 383 $R $R 4e18 $X $TH 113 rref=$R done=runs/R${R}_$X.done >> runs/R${R}_$X.log 2>&1
done

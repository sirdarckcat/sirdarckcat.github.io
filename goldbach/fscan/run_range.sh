#!/bin/bash
# run_range.sh Xmin Xmax R1 R2 ... : one fscan pass per residual class over Xmin < N <= Xmax, resumable.
# Progress in runs/R<R>_<Xmin>_<Xmax>.done, output appended to runs/R<R>_<Xmin>_<Xmax>.log.
# Thresholds: theta = 99 at R = 194 plus one per class, Ta = 113, score primes up to 383.
XMIN=$1; XMAX=$2; shift 2
cd "$(dirname "$0")"
mkdir -p runs
for R in "$@"; do
  TH=$((99 + R - 194))
  ./fscan 10007 383 $R $R $XMIN $XMAX $TH 113 rref=$R done=runs/R${R}_${XMIN}_${XMAX}.done >> runs/R${R}_${XMIN}_${XMAX}.log 2>&1
done

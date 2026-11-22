#!/bin/sh
# Compare three things on the same inputs: the fermat28 kernel source compiled for the CPU (each
# of the three generated step files), big-integer arithmetic in Python, and the Lean model Gpu28.
#   sh scripts/gpu28_check/run.sh path/to/goldbach/fermat661/cuda        (from goldbach/lean)
set -e
T=$(mktemp -d)
(cd "$T" && python3 -I "$OLDPWD/scripts/gpu28_check/gen_tests.py")
for f in fermat28_step_s1.cuh fermat28_step.cuh fermat28_step_s4.cuh; do
  g++ -O2 -w -DSTEPFILE="\"$f\"" -I "$1" -o "$T/harness" scripts/gpu28_check/harness.cpp
  "$T/harness" < "$T/tests.txt" > "$T/c_out.txt"
  cmp "$T/c_out.txt" "$T/expected.txt" && echo "$f: kernel (CPU build) = big-integer reference on $(wc -l < "$T/tests.txt") tests"
  lake env lean --run scripts/gpu28_check/cmp.lean "$T/tests.txt" "$T/c_out.txt"
done

#!/bin/sh
# Compare three things on the same inputs: the fermat28 kernel source compiled for the CPU (every
# generated step file, plain and redundant), big-integer arithmetic in Python, and the Lean model.
#   sh scripts/gpu28_check/run.sh path/to/goldbach/fermat661/cuda        (from goldbach/lean)
set -e
T=$(mktemp -d)
(cd "$T" && python3 -I "$OLDPWD/scripts/gpu28_check/gen_tests.py")
for f in fermat28_step_s1.cuh fermat28_step.cuh fermat28_step_s4.cuh fermat28_step_s1w.cuh fermat28_step_w.cuh \
         fermat28_step_s1r.cuh fermat28_step_r.cuh fermat28_step_s1rw.cuh; do
  [ -f "$1/$f" ] || { echo "$f: not in $1, skipped"; continue; }
  case "$f" in *r.cuh|*rw.cuh) mode=red;; *) mode=plain;; esac
  g++ -O2 -w -DSTEPFILE="\"$f\"" -I "$1" -o "$T/harness" scripts/gpu28_check/harness.cpp
  "$T/harness" < "$T/tests.txt" > "$T/c_out.txt"
  cmp "$T/c_out.txt" "$T/expected_$mode.txt" && echo "$f ($mode): kernel (CPU build) = big-integer reference on $(wc -l < "$T/tests.txt") tests"
  lake env lean --run scripts/gpu28_check/cmp.lean "$T/tests.txt" "$T/c_out.txt" $mode
done

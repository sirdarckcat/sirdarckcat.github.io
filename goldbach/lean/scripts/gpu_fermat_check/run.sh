#!/bin/sh
# Compare three things on the same inputs: the kernel source of gpu_fermat.py compiled for the
# CPU, a Python reference (pow), and the Lean model Gpu.fermat2 / Gpu.montSqr / Gpu.dblMod.
#   sh scripts/gpu_fermat_check/run.sh path/to/gpu_fermat.py path/to/spec.json    (from goldbach/lean)
set -e
T=$(mktemp -d)
python3 scripts/gpu_fermat_check/mkharness.py "$1" "$T/harness.c"
gcc -O2 -w -o "$T/harness" "$T/harness.c"
(cd "$T" && python3 "$OLDPWD/scripts/gpu_fermat_check/gen_tests.py" "$2")
"$T/harness" < "$T/tests.txt" > "$T/c_out.txt"
cmp "$T/c_out.txt" "$T/expected.txt" && echo "kernel (CPU build) = Python reference on $(wc -l < "$T/tests.txt") tests"
lake env lean --run scripts/gpu_fermat_check/cmp.lean "$T/tests.txt" "$T/c_out.txt"

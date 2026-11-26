#!/bin/bash
# Can the sieve run beside the Fermat kernel?  bench_overlap.py on ONE GPU (production paused on it), one text file.
#
#     RTX PRO 6000 (the 23 Nov 08:04Z probe: the default configuration works, x1.20 projected):
#         cd goldbach/sieve200/cuda && GPU=0 bash run_overlap_probe.sh /path/to/specs_variants.json [overlap_probe.txt]
#     L4 / T4 / A100 (the 'w' kernel; Fermat is 5x slower there, so fewer tests; 3 configurations, ~3 minutes):
#         VARIANT=s1rw TESTS=16777216 MODE=fleet GPU=0 bash run_overlap_probe.sh /path/to/specs_variants.json [overlap_probe.txt]
#
# Use a Q = 170,000 spec (the first variant's rows are used).  Reading: the last two lines of each block ("production batch ... -> xN.NN" and the verdict).
# Production batch times for the projection: PROJ="--proj-fermat F --proj-sieve S --proj-other O" (RTX default 1.27 / 0.43 / 0.06; an L4 batch of 9.5 s is ~6.1 / 3.4 / 0.0).
set -u
SPEC=${1:?usage: GPU=0 bash run_overlap_probe.sh SPEC.json [OUT.txt]}
GPU=${GPU:-0}
OUT=${2:-overlap_probe_$(hostname)_gpu${GPU}.txt}
VARIANT=${VARIANT:-s1r_asm}          # the production Fermat kernel of this GPU type (s1r_asm: RTX PRO 6000; s1rw: L4 / T4 / A100)
TESTS=${TESTS:-67108864}             # Fermat tests in the timed launch (~3 s)
MODE=${MODE:-full}                   # full: five configurations; fleet: the three that matter
PROJ=${PROJ:-}
export CUDA_VISIBLE_DEVICES=$GPU
HERE=$(cd "$(dirname "$0")" && pwd)
SPEC=$(readlink -f "$SPEC")
cd "$HERE" || exit 1
exec > >(tee "$OUT") 2>&1
nvidia-smi -i "$GPU" --query-gpu=name,driver_version,clocks.max.sm --format=csv
run() { echo; echo "=================================================================== $*"; date -u +"%Y-%m-%dT%H:%M:%SZ"; timeout 900 python3 bench_overlap.py "$SPEC" --tests "$TESTS" --ref-variant "$VARIANT" $PROJ "$@" || echo "FAILED: bench_overlap $*"; }
run --variant "$VARIANT"                                                           # production kernel, driver defaults, sieve stream of the highest priority (RTX PRO 6000: x1.20 projected)
run --variant "$VARIANT" --no-priority                                             # the same with a plain non-blocking stream: the sieve gets no SM time on the RTX (0 windows)
if [ "$MODE" = full ]; then
    run --variant "$VARIANT" --carveout 100                                        # every kernel asks for the largest shared-memory carve-out (no change on the RTX)
    run --variant s1r_asm_r80 --carveout 100                                       # 80 registers: 14k registers an SM stay free beside 5 Fermat CTAs (worse on the RTX)
    run --variant "$VARIANT" --carveout 100 --cta-sm 4                             # chunked Fermat launches (4 of the 5 CTAs an SM): sieve x2.0, Fermat 7% slower alone (x1.64 projected on the RTX)
else
    run --variant "$VARIANT" --cta-sm 4                                            # leaves a CTA's room on every SM for the sieve
fi
echo; echo "done"; date -u +"%Y-%m-%dT%H:%M:%SZ"

#!/bin/bash
# Can the sieve run beside the Fermat kernel?  Five configurations of bench_overlap.py on ONE GPU (production paused on it), ~4 minutes, one text file:
#
#     cd goldbach/sieve200/cuda && GPU=0 bash run_overlap_probe.sh /path/to/specs_variants.json [overlap_probe.txt]
#
# Use a Q = 170,000 spec (the first variant's rows are used).  Reading: the last two lines of each block ("production batch ... -> xN.NN" and the verdict).
set -u
SPEC=${1:?usage: GPU=0 bash run_overlap_probe.sh SPEC.json [OUT.txt]}
GPU=${GPU:-0}
OUT=${2:-overlap_probe_$(hostname)_gpu${GPU}.txt}
export CUDA_VISIBLE_DEVICES=$GPU
HERE=$(cd "$(dirname "$0")" && pwd)
SPEC=$(readlink -f "$SPEC")
cd "$HERE" || exit 1
exec > >(tee "$OUT") 2>&1
nvidia-smi -i "$GPU" --query-gpu=name,driver_version,clocks.max.sm --format=csv
run() { echo; echo "=================================================================== $*"; date -u +"%Y-%m-%dT%H:%M:%SZ"; timeout 900 python3 bench_overlap.py "$SPEC" "$@" || echo "FAILED: bench_overlap $*"; }
run                                                                                # production kernel, driver defaults: expected ~ no overlap (the 03:10Z trial)
run --carveout 100                                                                 # every kernel asks for the largest shared-memory carve-out
run --variant s1r_asm_r80 --carveout 100                                           # 80 registers: 14k registers an SM stay free beside 5 Fermat CTAs
run --variant s1r_asm_r80 --carveout 100 --no-priority                             # the same without the stream priority
run --carveout 100 --cta-sm 4                                                      # chunked Fermat launches (4 of the 5 CTAs an SM), as search_gpu5 --fermat-cta-sm 4
echo; echo "done"; date -u +"%Y-%m-%dT%H:%M:%SZ"

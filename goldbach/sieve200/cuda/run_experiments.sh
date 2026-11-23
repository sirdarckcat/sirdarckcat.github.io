#!/bin/bash
# Every experiment the uarch session is waiting for on ONE GPU, unattended, in one text file (about 20-25 minutes; production paused on that GPU):
#
#     cd goldbach/sieve200/cuda && GPU=0 bash run_experiments.sh /path/to/specs_variants.json [experiments_rtx.txt]
#
# A. the large-prime stage: bench_bigprimes plain against the STAGED kernel (gbig_gen_st; --check first), then sweep_bigprimes.sh (staged rows a CTA / marks staged / CTA size, rg, tile, ppt)
# B. the whole 2^25-member batch at B = 1e8: plain, staged, staged with 1024-thread tile CTAs, tile 2^18 (bench_batch.py: per-phase times)
# C. the Fermat step inside the real kernel: bench_fm28_step.py (loop-body size, extra IADD3 / IMAD.WIDE, occupancy) for the RTX's and the A100 / L4's step styles
# D. bench_pipes.py --warps: do the instruction costs shrink with more warps a scheduler?
# E. Nsight Compute on the Fermat kernel, if `ncu` works on this host (stall reasons, issue slots, pipe utilisation)
# F. bench_clock.py: does clock64() tick at the SM clock?  (5 seconds; every "cycle" of the pipe benchmarks is a clock64 difference)
# G. the production Fermat step with 1, 2 and 4 independent accumulators a column (time_fermat28.py, ~1 minute): if the RTX step is latency bound the 2 and 4 are faster; the cost model says -2.5% / -7%
# SECTIONS="B C" runs only those; every section is time-limited and a failure does not stop the next one.  Then: summarize / commit the file and tell the uarch session.
set -u
SPEC=${1:?usage: GPU=0 bash run_experiments.sh SPEC.json [OUT.txt]}
GPU=${GPU:-0}
OUT=${2:-experiments_$(hostname)_gpu${GPU}.txt}
SECTIONS=${SECTIONS:-"F G A B C D E"}
export CUDA_VISIBLE_DEVICES=$GPU
HERE=$(cd "$(dirname "$0")" && pwd)
FC=$HERE/../../fermat661/cuda
SPEC=$(readlink -f "$SPEC")
cd "$HERE" || exit 1
exec > >(tee "$OUT") 2>&1
want() { case " $SECTIONS " in *" $1 "*) return 0;; *) return 1;; esac; }
section() { echo; echo "=================================================================== $*"; date -u +"%Y-%m-%dT%H:%M:%SZ"; }
nvidia-smi -i "$GPU" --query-gpu=name,driver_version,power.limit,clocks.max.sm --format=csv

if want F; then
  section "F. is clock64() the SM clock?  (ticks per ns of %globaltimer, ticks per dependent IMAD: 4 expected; the SM clock is sampled beside it)"
  nvidia-smi -i "$GPU" --query-gpu=clocks.sm --format=csv,noheader,nounits -lms 200 > /tmp/exp_clk_$$.csv 2>/dev/null &
  SAMP=$!
  timeout 300 python3 bench_clock.py || echo "FAILED: bench_clock"
  kill $SAMP 2>/dev/null; wait $SAMP 2>/dev/null
  python3 - /tmp/exp_clk_$$.csv <<'PY'
import sys, statistics
v = [float(x) for x in open(sys.argv[1]).read().split() if x.replace('.', '', 1).isdigit()]
if len(v) > 4:
    v = v[1:-1]
    print(f"  nvidia-smi SM clock during the run: median {statistics.median(v):.0f} MHz, min {min(v):.0f}, max {max(v):.0f}")
PY
  rm -f /tmp/exp_clk_$$.csv
fi

if want G; then
  section "G. accumulators a column: s1r_asm (production) against s2r_asm and s4r_asm (tests/s, --check against gmpy2; the cost model for a throughput-bound step: -2.5% and -7%)"
  timeout 900 python3 "$FC/time_fermat28.py" "$SPEC" --variant s1r_asm s2r_asm s4r_asm --seconds 15 --check || echo "FAILED: time_fermat28 s2r_asm / s4r_asm"
fi

if want A; then
  section "A. large-prime stage: plain against staged (B = 2^24, 1,093 rows, 8 groups of 16 rows, batch 2^25)"
  echo "--- plain"
  timeout 900 python3 bench_bigprimes.py --b 24 --groups 8 || echo "FAILED: bench_bigprimes plain"
  echo "--- staged, check against numpy first (must say identical)"
  timeout 900 python3 bench_bigprimes.py --rows 40 --b 22 --ks 25 --check --staged 1 || echo "FAILED: bench_bigprimes staged check"
  echo "--- staged (2 rows a CTA, 8192 marks staged, 256 threads)"
  timeout 900 python3 bench_bigprimes.py --b 24 --groups 8 --staged 1 || echo "FAILED: bench_bigprimes staged"
  echo "--- the same at B = 2^28"
  timeout 1800 python3 bench_bigprimes.py --b 28 --groups 2 || echo "FAILED: bench_bigprimes plain b28"
  timeout 1800 python3 bench_bigprimes.py --b 28 --groups 2 --staged 1 || echo "FAILED: bench_bigprimes staged b28"
  echo "--- sweep_bigprimes.sh (its own table)"
  timeout 2400 bash sweep_bigprimes.sh /dev/null || echo "FAILED: sweep_bigprimes"
fi

if want B; then
  section "B. the whole batch pipeline at B = 1e8, per-phase ms (bench_batch.py; a batch of 2^25 members, 1,09x rows)"
  for cfg in "--staged 0" "--staged 1" "--staged 1 --tile-threads 1024" "--staged 1 --tile 18" "--staged 0 --tile-threads 1024"; do
    echo "--- $cfg"
    timeout 2400 python3 bench_batch.py "$SPEC" --B 100000000 --ks 25 $cfg || echo "FAILED: bench_batch $cfg"
  done
fi

if want C; then
  section "C. the Fermat step inside the real kernel (bench_fm28_step.py): E1 loop-body size, E2 extra instructions, E3 occupancy (the GHz column: clock64 ticks per ns of event time, to compare with the SM clock sampled beside it)"
  nvidia-smi -i "$GPU" --query-gpu=clocks.sm --format=csv,noheader,nounits -lms 200 > /tmp/exp_clkC_$$.csv 2>/dev/null &
  SAMPC=$!
  for st in s1r_asm s1rw; do
    echo "--- style $st"
    timeout 1500 python3 "$FC/bench_fm28_step.py" --style $st || echo "FAILED: bench_fm28_step $st"
  done
  kill $SAMPC 2>/dev/null; wait $SAMPC 2>/dev/null
  python3 - /tmp/exp_clkC_$$.csv <<'PY'
import sys, statistics
v = [float(x) for x in open(sys.argv[1]).read().split() if x.replace('.', '', 1).isdigit()]
v = [x for x in v if x > 500]                      # idle samples between launches are low
if len(v) > 4:
    print(f"  nvidia-smi SM clock during section C (samples above 500 MHz): median {statistics.median(v):.0f} MHz, min {min(v):.0f}, max {max(v):.0f}")
PY
  rm -f /tmp/exp_clkC_$$.csv
fi

if want D; then
  section "D. bench_pipes.py --warps: cycles an instruction costs a scheduler against the warps a scheduler"
  timeout 900 python3 bench_pipes.py --warps || echo "FAILED: bench_pipes --warps"
fi

if want E; then
  section "E. Nsight Compute on the Fermat kernel (skipped if ncu is missing or refused)"
  if command -v ncu >/dev/null 2>&1; then
    ncu --version | head -3
    timeout 900 ncu --section SchedulerStats --section WarpStateStats --section ComputeWorkloadAnalysis --section InstructionStats --section LaunchStats --section Occupancy \
        -k regex:fermat28 --launch-count 1 python3 "$FC/time_fermat28.py" "$SPEC" --variant s1r_asm --seconds 2 || echo "FAILED: ncu (counters may be restricted: ERR_NVGPUCTRPERM)"
  else
    echo "ncu not found"
  fi
fi

section "done"
echo "output file: $OUT"

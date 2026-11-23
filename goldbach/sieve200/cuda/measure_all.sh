#!/bin/bash
# Everything the uarch session is waiting for, on ONE GPU, in one text file.  Run it with production paused on that GPU:
#
#     cd goldbach/sieve200/cuda && GPU=0 bash measure_all.sh /path/to/specs_variants.json [measure_a100.txt]
#
# SPEC = the spec file you give test_gpu_fermat28.py / test_gpu_sieve.py (a campaign spec {"N0","M","residual","cover"}, or a list of them: the first is used).
# Needs what those need (cupy, numpy, gmpy2, gcc), ~8 GB of free GPU memory, about 10-20 minutes.  Every section is time-limited and a failure does not stop the next one.
# GPU = the physical index for nvidia-smi and CUDA_VISIBLE_DEVICES (default 0).  Run it once per GPU TYPE (RTX PRO 6000, A100, L4).
#
# Sections: 1 GPU, clocks, power limit.  2 the Fermat kernels (s1r asm = the RTX PRO 6000s' kernel, s1rw = the A100 / L4's) for 20 s each with the SM clock, power and throttle
# reasons sampled beside them (this is what decides whether the RTX PRO 6000s are power-clocked).  3 bench_pipes part 3 (the global-memory cost of a scattered mark).
# 4 bench_bigprimes (the large-prime stage of a deeper sieve bound: ns a mark).  5 test_gpu_sieve (the sieve against the CPU feeder + the sweep of the new options, clock sampled).
# 6 bench_batch (the whole batch pipeline of a deeper bound at production size).
# Afterwards: commit the output file to your branch (or send it) and tell the uarch session where it is.
set -u
SPEC=${1:?usage: GPU=0 bash measure_all.sh SPEC.json [OUT.txt]}
GPU=${GPU:-0}
OUT=${2:-measure_$(hostname)_gpu${GPU}.txt}
export CUDA_VISIBLE_DEVICES=$GPU
HERE=$(cd "$(dirname "$0")" && pwd)
FC=$HERE/../../fermat661/cuda
SPEC=$(readlink -f "$SPEC")
cd "$HERE" || exit 1
exec > >(tee "$OUT") 2>&1

if nvidia-smi -i "$GPU" --query-gpu=clocks_event_reasons.active --format=csv,noheader >/dev/null 2>&1; then REASON=clocks_event_reasons.active; else REASON=clocks_throttle_reasons.active; fi
SAMPLER=""
sample_start() {                       # $1: csv file
  nvidia-smi -i "$GPU" --query-gpu=clocks.sm,clocks.max.sm,power.draw,power.limit,temperature.gpu,$REASON --format=csv,noheader,nounits -lms 500 > "$1" 2>/dev/null &
  SAMPLER=$!
}
sample_stop() {                        # $1: csv file; prints median / min / max SM clock, power, temperature, throttle-reason words
  [ -n "$SAMPLER" ] && kill "$SAMPLER" 2>/dev/null && wait "$SAMPLER" 2>/dev/null
  SAMPLER=""
  python3 - "$1" <<'PY'
import sys, statistics, collections
rows = []
for line in open(sys.argv[1]):
    f = [x.strip() for x in line.split(",")]
    if len(f) >= 6:
        rows.append(f)
rows = rows[2:-1] if len(rows) > 6 else rows
def num(i):
    out = []
    for r in rows:
        try: out.append(float(r[i]))
        except ValueError: pass
    return out
if not rows:
    print("  (no nvidia-smi samples)")
else:
    c, p, t = num(0), num(2), num(4)
    reasons = collections.Counter(r[5] for r in rows)
    print(f"  SM clock MHz: median {statistics.median(c):.0f}  min {min(c):.0f}  max {max(c):.0f}  (max allowed {rows[0][1]})   [{len(rows)} samples]")
    if p: print(f"  power W: median {statistics.median(p):.0f}  max {max(p):.0f}  (limit {rows[0][3]})   temperature C: median {statistics.median(t):.0f}" if t else f"  power W: median {statistics.median(p):.0f}")
    print("  throttle/event reasons (bit mask: count):", dict(reasons))
PY
}
section() { echo; echo "=================================================================== $*"; date -u +"%Y-%m-%dT%H:%M:%SZ"; }

section "1. GPU"
nvidia-smi -i "$GPU" --query-gpu=name,driver_version,memory.total,pstate,power.limit,power.max_limit,clocks.max.sm,clocks.max.mem --format=csv
nvidia-smi -i "$GPU" -q -d CLOCK,POWER 2>/dev/null | head -70
python3 -c "import cupy, numpy; print('cupy', cupy.__version__, 'numpy', numpy.__version__, 'cuda runtime', cupy.cuda.runtime.runtimeGetVersion())"

section "2. Fermat kernels with the SM clock and power sampled beside them (20 s each)"
for v in s1r_asm s1rw; do
  echo "--- $v"
  sample_start /tmp/measure_clk_$$.csv
  timeout 600 python3 "$FC/time_fermat28.py" "$SPEC" --variant $v --seconds 20 --check || echo "FAILED: time_fermat28.py $v"
  sample_stop /tmp/measure_clk_$$.csv
done

section "3. bench_pipes.py part 3: scattered marks in global memory"
timeout 900 python3 bench_pipes.py --part3 || echo "FAILED: bench_pipes part 3"

section "4. bench_bigprimes.py: the large-prime stage of a deeper sieve bound"
timeout 900 python3 bench_bigprimes.py --rows 40 --b 22 --ks 25 --check || echo "FAILED: bench_bigprimes check"
timeout 1200 python3 bench_bigprimes.py --b 24 --groups 8 || echo "FAILED: bench_bigprimes b24"
timeout 1200 python3 bench_bigprimes.py --b 26 --groups 4 || echo "FAILED: bench_bigprimes b26"
timeout 1800 python3 bench_bigprimes.py --b 28 --groups 2 || echo "FAILED: bench_bigprimes b28"

section "5. test_gpu_sieve.py: the GPU sieve against the CPU feeder, per-phase times, sweep of the options (SM clock sampled)"
sample_start /tmp/measure_clk_$$.csv
timeout 1800 python3 test_gpu_sieve.py "$SPEC" --B 1000000 --klog 19 --f 0.97 || echo "FAILED: test_gpu_sieve"
sample_stop /tmp/measure_clk_$$.csv

section "6. bench_batch.py: the whole batch pipeline of a deeper sieve bound at production size (B = 2^26, a batch of 2^25 members)"
timeout 2400 python3 bench_batch.py "$SPEC" --B 67108864 --ks 25 --check || echo "FAILED: bench_batch"

section "done"
rm -f /tmp/measure_clk_$$.csv
echo "output file: $OUT"

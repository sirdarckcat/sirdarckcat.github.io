#!/bin/bash
# Every CPU-only test of the sieve and Fermat code (no GPU, no cupy: the kernels run as g++-compiled emulations, cupy is a numpy stand-in), one line each.  ~30-40 minutes on a 48-core box.
#   bash run_cpu_tests.sh [quick]        quick: only the fast ones (a few minutes)
cd "$(dirname "$0")"
QUICK=$1
fail=0
t() {   # label, command...  (run in sieve200/cuda or fermat661/cuda: the command is prefixed by `cd dir &&`)
    local label=$1 dir=$2; shift 2
    local t0=$(date +%s)
    if (cd "$dir" && timeout 3600 env "$@" > /tmp/cputest_$$.log 2>&1); then st=PASS; else st=FAIL; fail=$((fail+1)); fi
    printf "%-4s %-70s %4ds\n" $st "$label" $(( $(date +%s) - t0 ))
    [ $st = FAIL ] && tail -n 6 /tmp/cputest_$$.log | cut -c1-200
}
S=sieve200/cuda; F=fermat661/cuda
t "fused rounds vs the driver's run_pool"          $F python3 test_fround_cpu.py
t "step benchmark glue (fake GPU), E1-E5"          $F python3 test_bench_fm28_step_fake.py
t "head accounting simulation"                     $S python3 test_head_accounting.py
t "bench_split glue"                               $S python3 test_bench_split_cpu.py
t "large-prime stage vs numpy (+packed, fallback)" $S python3 test_gbig_cpu.py
t "large-prime stage, hoisted + unroll 2"          $S DEEP_GEN_HOIST=1 DEEP_GEN_UNROLL=2 python3 test_gbig_cpu.py
t "staged kernel vs brute force: every variant"    $S python3 test_gbig.py
t "large-prime stage, flat flush + grid order"     $S DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_HOIST=1 DEEP_GEN_UNROLL=4 python3 test_gbig_cpu.py
[ "$QUICK" = quick ] && { echo "quick: $fail failure(s)"; exit $fail; }
t "GPU sieve vs CPU feeder"                        $S python3 test_gpu_sieve_cpu.py
t "batch sieve vs CPU feeder"                      $S python3 test_gbatch_cpu.py
t "batch sieve, packed bins"                       $S DEEP_BIN_PACK=1 python3 test_gbatch_cpu.py
t "batch sieve, hoist + packed + gen unroll 4"     $S DEEP_GEN_HOIST=1 DEEP_BIN_PACK=1 DEEP_GEN_UNROLL=4 python3 test_gbatch_cpu.py
t "batch sieve, tile unroll 4"                     $S DEEP_TILE_UNROLL=4 python3 test_gbatch_cpu.py
t "batch sieve, flat flush + grid order"           $S DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 python3 test_gbatch_cpu.py
t "batch sieve, flat flush (alone)"                $S DEEP_GEN_FLUSH2=1 python3 test_gbatch_cpu.py
t "batch sieve, packed + flat flush"               $S DEEP_BIN_PACK=1 DEEP_GEN_FLUSH2=1 python3 test_gbatch_cpu.py
t "batch sieve, everything (pack hoist unroll 4 flush2 order)" $S DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_UNROLL=4 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 python3 test_gbatch_cpu.py
t "deferred overflow check"                        $S python3 test_gbatch_defer_cpu.py
t "deferred overflow check, packed"                $S DEEP_BIN_PACK=1 python3 test_gbatch_defer_cpu.py
t "DeepSieve over variants"                        $S python3 test_deep_feeder_cpu.py
t "DeepSieve, staged + packed"                     $S DEEP_STAGED=1 DEEP_BIN_PACK=1 python3 test_deep_feeder_cpu.py
t "deep head vs brute force (+DeepSieve)"          $S python3 test_ghead_cpu.py
t "headcheck.py on the emulation"                  $S python3 test_headcheck_cpu.py
echo "$fail failure(s)"
exit $fail

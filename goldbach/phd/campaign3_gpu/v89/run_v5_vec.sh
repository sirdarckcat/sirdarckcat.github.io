#!/bin/bash
# campaign3 in vector mode (search_gpu5.py --vector-dir): short vectors (covers on 89 moduli, ~2.1e7 members a vector) from the chunk files of VDIR,
# one window of 2^klog members each from the first k with 200-digit N, k-range and window from DEEP_ARGS (e.g. --klog 24 --slice 16777216).
#   bash run_v5_vec.sh DIR VDIR
D=$1; V=$2
mkdir -p $D; cd $D
echo "$(date -u +%FT%TZ) start search_gpu5 vector campaign in $D, vectors from $V, f=${SKIPF:-0.97} kernel ${KERNEL:-28} (${K28_STEP:-fermat28_step_s1r.cuh} asm ${K28_ASM:-1})${DEEP_ARGS:+ deep: $DEEP_ARGS}" >> driver.log
python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $V --goldbach /content/c3g --batch ${BATCH:-4} --pool ${POOL:-2097152} \
  --skip-frac ${SKIPF:-0.97} --p-est 0.055 --no-stop --kernel ${KERNEL:-28} --sieve200 ${SIEVE200} --sieve-threads ${SIEVE_THREADS:-256} \
  --k28-step ${K28_STEP:-fermat28_step_s1r.cuh} --k28-asm ${K28_ASM:-1} --near-miss ${NEAR_MISS:-0} ${DEEP_ARGS:-} >> driver.log 2>&1
echo "C3GPU-END rc=$? $(date -u +%FT%TZ)" >> driver.log

#!/bin/bash
# The L4 that replaces the A100: install, check the kernels against gmpy2 (test28_prod.py, w set), the pipeline (check_v5w.sh:
# kernel 3 against kernel 28 s1rw on 12 production slices) and the deep sieve (check_deep.sh: --deep at B = 10^6 identical to the
# normal path, B = 10^8 sane) on this GPU, then the Q = 150,000 campaign in deep mode on its vectors, k in [2^30, 2^32).
mkdir -p /content/c3g /content/c150 /content/bp /content/f28w /content/ua57
cd /content/c3g && tar -xzf /content/c3g_bundle2.tgz && cp run_v5_campQ.sh /content/run_v5_campQ.sh && cp search_gpu5.py /content/search_gpu5_deep.py && cp check_deep.sh /content/check_deep.sh
cd /content/bp && tar -xzf /content/bp.tgz
cd /content/f28w && tar -xzf /content/cuda28w.tgz
cd /content/ua57 && tar -xzf /content/ua57b.tgz
pip install -q gmpy2 sympy > /content/pip.log 2>&1
cd /content/c3g && FERMAT28_DIR=/content/f28w timeout 1500 python3 test28_prod.py /content/c150/my_specs.json 40000 2097152 w > /content/c3g/test28.out 2>&1
echo "/content/c150" > /content/next_campaign_dir
echo "KLO=1073741824 KERNEL=3 SKIPF=0.97 BATCH=64 POOL=2097152 SIEVE200=/content/bp/goldbach/sieve200 SIEVE_THREADS=1024" > /content/next_campaign_env
echo "KERNEL=28 K28_STEP=fermat28_step_s1rw.cuh K28_ASM=0 FERMAT28_DIR=/content/f28w" > /content/k28w_env
bash /content/c3g/check_v5w.sh
echo "KLO=1073741824 KERNEL=28 SKIPF=0.97 BATCH=64 POOL=2097152 SIEVE200=/content/bp/goldbach/sieve200 SIEVE_THREADS=1024 K28_STEP=fermat28_step_s1rw.cuh K28_ASM=0 FERMAT28_DIR=/content/f28w" > /content/next_campaign_env
bash /content/check_deep.sh
if ! grep -q "ALL MATCH" /content/c3g/test28.out || ! grep -q "CHECKW PASSED" /content/k28w_check/check.txt || ! grep -q "DEEPCHECK PASSED" /content/deepcheck/result.txt; then
  echo "C3GPU-END rc=99 checks failed on this GPU $(date -u +%FT%TZ)" >> /content/c150/driver.log; exit 1; fi
echo "$(date -u +%FT%TZ) checks passed on this L4 ($(hostname)): test28_prod w ALL MATCH; check_v5w kernel 3 = kernel 28 s1rw; check_deep PASSED" >> /content/c150/driver.log
echo "KLO=1073741824 KERNEL=28 SKIPF=0.97 BATCH=2 POOL=2097152 SIEVE200=/content/ua57/goldbach/sieve200 SIEVE_THREADS=1024 K28_STEP=fermat28_step_s1rw.cuh K28_ASM=0 FERMAT28_DIR=/content/f28w" > /content/next_campaign_env
cp /content/deep_env_src /content/deep_env
env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh /content/c150

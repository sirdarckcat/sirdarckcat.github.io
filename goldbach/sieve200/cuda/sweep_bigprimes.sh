#!/bin/bash
# What limits the large-prime stage (bench_bigprimes.py: pass B writes the marks into bins)?  One GPU, production paused, ~5 minutes:
#     cd goldbach/sieve200/cuda && GPU=0 bash sweep_bigprimes.sh [OUT.txt]
# Each line: the configuration and ns a mark of gen (pass A + pass B), apply, total, and pass B alone.  ppt = primes a thread (longer runs per bin when large),
# rg = rows a CTA group (bins = rg x 64), threads = CTA size of gen.  B = 2^24 (1,093 rows, 8 groups), batch 2^25.
set -u
GPU=${GPU:-0}
OUT=${1:-sweep_bigprimes_$(hostname)_gpu${GPU}.txt}
export CUDA_VISIBLE_DEVICES=$GPU
cd "$(dirname "$0")" || exit 1
exec > >(tee "$OUT") 2>&1
run() {   # label, args...
  local label=$1; shift
  printf '%-34s ' "$label"
  timeout 600 python3 bench_bigprimes.py --b 24 --groups 8 "$@" 2>&1 | awk '/ns a mark:/ {g=$5; a=$7; t=$9} /of gen:/ {for (i=1;i<=NF;i++) if ($i=="pass" && $(i+1)=="B") {pb=$(i+8)}} /Error|error|Traceback/ {err=1} END {if (err) print "FAILED"; else printf "gen %s apply %s total %s ns/mark; pass B %s\n", g, a, t, pb}'
}
run "ppt 4 rg 16 thr 256 (default)" --ppt 4 --rg 16 --threads 256
for ppt in 1 2 8 16 32; do run "ppt $ppt rg 16 thr 256" --ppt $ppt --rg 16 --threads 256; done
for rg in 4 8 32; do run "ppt 4 rg $rg thr 256" --ppt 4 --rg $rg --threads 256; done
for thr in 128 512 1024; do run "ppt 4 rg 16 thr $thr" --ppt 4 --rg 16 --threads $thr; done
run "ppt 16 rg 4 thr 256" --ppt 16 --rg 4 --threads 256
run "ppt 16 rg 32 thr 512" --ppt 16 --rg 32 --threads 512
echo "done"

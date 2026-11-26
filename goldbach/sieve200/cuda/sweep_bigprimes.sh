#!/bin/bash
# What limits the large-prime stage (bench_bigprimes.py: pass B writes the marks into bins; apply reads them)?  One GPU, production paused, ~6 minutes:
#     cd goldbach/sieve200/cuda && GPU=0 bash sweep_bigprimes.sh [OUT.txt]
# Each line: the configuration, and ns a mark of gen (pass A + pass B), apply, total, and pass B alone (B = 2^24, 1,093 rows, batch 2^25; a few groups timed and scaled).
#   ppt   = primes a thread: longer runs per bin (and per CTA) when large.
#   rg    = rows a group: the bins of a group are rg x 2^(25 - tile) bins of `cap` entries (430 MB at rg 16): small rg makes them fit the L2 cache (~128 MB), at the price of reading
#           the prime table (91 MB at B = 1e8) once a group.
#   tile  = log2 of the bits of a tile (the shared bitmap of the apply kernel): 17 / 18 / 19 = 16 / 32 / 64 KB, two to eight times more (smaller) bins.
#   thr   = CTA size of gen.
set -u
GPU=${GPU:-0}
OUT=${1:-sweep_bigprimes_$(hostname)_gpu${GPU}.txt}
export CUDA_VISIBLE_DEVICES=$GPU
cd "$(dirname "$0")" || exit 1
exec > >(tee "$OUT") 2>&1
run() {   # label, groups, args...
  local label=$1 groups=$2; shift 2
  printf '%-40s ' "$label"
  timeout 600 python3 bench_bigprimes.py --b 24 --groups "$groups" "$@" 2>&1 | awk '/ns a mark:/ {g=$5; a=$7; t=$9} /of gen:/ {for (i=1;i<=NF;i++) if ($i=="pass" && $(i+1)=="B") {pb=$(i+8)}} /Error|error|Traceback/ {err=1} END {if (err) print "FAILED"; else printf "gen %s apply %s total %s ns/mark; pass B %s\n", g, a, t, pb}'
}
echo "--- the STAGED kernel (gbig_gen_st): marks sorted by bin in shared memory, whole runs written; rcta = rows a CTA, stage = marks staged a CTA, thr = CTA size"
for rcta in 1 2 4; do for sc in 4096 8192 11000; do run "staged rcta $rcta stage $sc thr 256" 8 --staged 1 --rcta $rcta --stage-cap $sc --threads 256; done; done
for thr in 128 512 1024; do run "staged rcta 2 stage 8192 thr $thr" 8 --staged 1 --rcta 2 --stage-cap 8192 --threads $thr; done
run "staged rcta 2 stage 8192 rg 4" 8 --staged 1 --rcta 2 --stage-cap 8192 --rg 4
run "staged rcta 2 stage 8192 tile 18" 8 --staged 1 --rcta 2 --stage-cap 8192 --tile 18 --threads 256
echo "--- the plain kernel: the default and the primes a thread"
run "ppt 4 rg 16 tile 19 thr 256 (default)" 8 --ppt 4 --rg 16 --threads 256
for ppt in 1 2 8 16 32; do run "ppt $ppt rg 16 tile 19" 8 --ppt $ppt --rg 16; done
echo "--- rows a group (bins that fit the L2 cache)"
for rg in 1 2 4 8 32; do run "ppt 4 rg $rg tile 19" $((rg < 4 ? 32 : 8)) --ppt 4 --rg $rg; done
echo "--- tile size (more, smaller bins)"
for tile in 17 18; do for rg in 2 4 16; do run "ppt 4 rg $rg tile $tile" 8 --ppt 4 --rg $rg --tile $tile; done; done
echo "--- CTA size of gen"
for thr in 128 512 1024; do run "ppt 4 rg 16 tile 19 thr $thr" 8 --ppt 4 --rg 16 --threads $thr; done
echo "--- combinations"
run "ppt 16 rg 4 tile 19" 8 --ppt 16 --rg 4
run "ppt 16 rg 2 tile 18" 8 --ppt 16 --rg 2 --tile 18
run "ppt 8 rg 4 tile 18 thr 512" 8 --ppt 8 --rg 4 --tile 18 --threads 512
echo "done"

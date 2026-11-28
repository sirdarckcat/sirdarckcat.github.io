#!/bin/sh
# Look for a family of covers better than family B on the weighted rows: plain tempering on the first 89 odd primes from
# random starts at sharp thresholds around 170,000, every dump measured by family_eval.py (weighted rows as they are and
# with 463 replaced by every prime up to 590), near-misses polished.  One process per call; run several with different ids.
#
#   ./family_search/family_search.sh workdir id [sweeps=300000] [weights=family_search/weights_8.9days.txt]     (from cover/)
#
# Needs ./covergen (gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm) and a tempering binary: PTCOVER=path, default
# ./ptcover (the uarch session's ptcover_fast.c, goldbach/ptcover/ on branch ccr-b8c25887-i6tn9f, gives the same output twice
# as fast).  Results are appended to workdir/log.txt; lines starting with CANDIDATE are covers better than the best known.
W=$1; id=$2; SW=${3:-300000}; WF=${4:-family_search/weights_8.9days.txt}; PT=${PTCOVER:-./ptcover}
[ -n "$id" ] || { echo "usage: $0 workdir id [sweeps] [weights]" >&2; exit 1; }
mkdir -p "$W"; awk '{print $1}' first88.txt > "$W/m89_$id.mod" 2>/dev/null
python3 - "$W/m89_$id.mod" <<'PY'
import sys
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
open(sys.argv[1], "w").write("".join(f"{p}\n" for p in primes_upto(463) if p > 2))
PY
seed=$((40000 + id * 1000 + $(date +%s) % 900))
while true; do
  seed=$((seed + 1))
  Q=$((169500 + 500 * (seed % 4)))
  KD=$(( 1251 + (Q - 170000) * 86 / 10000 ))
  rm -f "$W/dump_$id.txt"
  PT_DUMP="$W/dump_$id.txt" PT_KDUMP=$KD OMP_NUM_THREADS=1 $PT $Q "$W/m89_$id.mod" $SW $seed betas56.txt > "$W/run_$id.txt" 2> "$W/run_$id.err"
  k=$(grep 'best k found' "$W/run_$id.txt" | awk '{print $NF}')
  echo "$(date -u +%FT%TZ) Q $Q seed $seed: best k $k (dump at <= $KD)" >> "$W/log.txt"
  [ -s "$W/dump_$id.txt" ] && python3 family_search/family_eval.py "$WF" "$W/dump_$id.txt" "Q$Q.seed$seed" >> "$W/log.txt" 2>&1
done

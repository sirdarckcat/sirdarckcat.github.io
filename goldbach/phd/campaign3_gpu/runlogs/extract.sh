#!/bin/bash
# Compact campaign records from a card's snapshot (snap.tgz or final_snap.tgz) into the repo: done sets (name@k0 a slice, xz), found files, generator ledgers (xz),
# the L4/T4 search logs (the top-16 levels ledger, xz) and a summary line. Usage: extract.sh CARD SNAPFILE OUTDIR
CARD=${1:?card}; SNAP=${2:?snapshot}; OUT="${3:?outdir}/${CARD}"
T=$(mktemp -d); mkdir -p "$OUT"; : > "$OUT/summary.txt"
tar -xzf "$SNAP" -C "$T" --wildcards 'c170*/search.log' 'c170*/found.jsonl' 'c170*/gpu3_stats.log' 'cover89/ledger_p*.txt' 'c150cpu/goldbach/phd/campaign3_hi*/found.jsonl' \
    'c150cpu/goldbach/phd/campaign3_hi*/search.log' 'vec89/made.txt' 'next_campaign_env' 'deep_env*' 2>/dev/null
for d in c170v c170 c170f; do
  [ -f "$T/$d/search.log" ] || continue
  grep -o '^\[[^]]*\]' "$T/$d/search.log" | tr -d '[]' | xz -9 > "$OUT/${d}_done.txt.xz"
  [ -s "$T/$d/found.jsonl" ] && cp "$T/$d/found.jsonl" "$OUT/${d}_found.jsonl"
  [ "$d" = c170f ] && xz -9 -c "$T/$d/search.log" > "$OUT/c170f_search.log.xz"
  n=$(grep -c '^\[' "$T/$d/search.log"); f=$(cat "$T/$d/found.jsonl" 2>/dev/null | wc -l); b=$(wc -l < "$T/$d/gpu3_stats.log" 2>/dev/null)
  eh=$(grep -o 'expected hits [0-9.e+-]*' "$T/$d/gpu3_stats.log" 2>/dev/null | awk '{s+=$3} END {printf "%.4e", s}')
  en=$(grep -o 'expected near>=[0-9]* [0-9.e+-]*' "$T/$d/gpu3_stats.log" 2>/dev/null | awk '{s+=$3} END {printf "%.4e", s}')
  echo "$CARD $d: $n slices, $b batches, found lines $f, expected design hits (sum) $eh, expected near-misses (sum, where logged) $en, first $(head -c 19 "$T/$d/gpu3_stats.log" 2>/dev/null) last $(tail -n 1 "$T/$d/gpu3_stats.log" 2>/dev/null | cut -c1-19)" >> "$OUT/summary.txt"
done
for f in "$T"/cover89/ledger_p*.txt; do [ -f "$f" ] && xz -9 -c "$f" > "$OUT/$(basename "$f").xz"; done
for f in "$T"/c150cpu/goldbach/phd/campaign3_hi*/found.jsonl; do [ -s "$f" ] && cp "$f" "$OUT/cpushare_$(basename "$(dirname "$f")")_found.jsonl"; done
for f in "$T"/c150cpu/goldbach/phd/campaign3_hi*/search.log; do [ -f "$f" ] && echo "$CARD cpu share $(basename "$(dirname "$f")"): $(grep -c '^\[' "$f") slices" >> "$OUT/summary.txt"; done
[ -f "$T/vec89/made.txt" ] && echo "$CARD vec89 made $(cat "$T/vec89/made.txt")" >> "$OUT/summary.txt"
cp "$T/next_campaign_env" "$OUT/next_campaign_env" 2>/dev/null; for f in "$T"/deep_env*; do [ -f "$f" ] && cp "$f" "$OUT/"; done
rm -rf "${T:?}"
du -sh "$OUT" | cut -f1

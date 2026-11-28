#!/bin/sh
# Improve the best known cover for target Q by repeated capped walks ("record-to-record travel"):
# walk in the set of covers with at most best+SLACK uncovered rows, keep every cover met that has at most `best`
# rows, lower `best` whenever a better one turns up, and go on from the best ones.  Stops after TRIES walks in a
# row without improvement.
#
#   ./descend.sh Q start.txt out.txt [tries=3] [seconds per walk=20] [slack=1]
#
# start.txt: "COVER k r:a ..." lines (ptcover, covergen or specs_to_covers.py).  out.txt receives the covers with
# the fewest uncovered rows found, same format; it can serve as starts/q<Q>.txt.
set -e
cd "$(dirname "$0")"
Q=$1; START=$2; OUT=$3; TRIES=${4:-3}; SECS=${5:-20}; SLACK=${6:-1}
[ -n "$OUT" ] || { echo "usage: $0 Q start.txt out.txt [tries] [seconds] [slack]" >&2; exit 1; }
[ -x ./covergen ] || gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
best=$(awk '$1=="COVER" && (m=="" || $2<m) {m=$2} END{print m}' "$START")
awk -v b="$best" '$1=="COVER" && $2==b' "$START" > "$W/cur.txt"
fail=0; seed=1
while [ $fail -lt "$TRIES" ]; do
    seed=$((seed + 1))
    COVERGEN_TIME=$SECS ./covergen "$Q" "$W/cur.txt" $((best + SLACK)) 100000000 $seed 2>/dev/null | awk -v b="$best" '$2<=b' > "$W/new.txt" || true
    nb=$(awk -v b="$best" '(m=="" || $2<m) {m=$2} END{print (m=="" ? b : m)}' "$W/new.txt")
    if [ "$nb" -lt "$best" ]; then
        best=$nb; fail=0
        awk -v b="$best" '$2==b' "$W/new.txt" > "$W/cur.txt"
    else
        fail=$((fail + 1))
        cat "$W/new.txt" >> "$W/cur.txt"                      # more covers at the same level to walk from
    fi
    echo "Q=$Q walk $seed: best $best, $(wc -l < "$W/cur.txt") covers at that level" >&2
done
sort -u "$W/cur.txt" > "$OUT"
echo "Q=$Q: best $best uncovered rows, $(wc -l < "$OUT") covers written to $OUT" >&2

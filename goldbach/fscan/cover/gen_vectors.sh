#!/bin/sh
# Search vectors in bulk: count new specs for target Q with at most kcap uncovered rows, best first.
#
#   ./gen_vectors.sh Q kcap count name [seed] [tag]      ->  specs_q<Q>[_<tag>]_<name>.json
#
# tag selects another family of starting covers, starts/q<Q>_<tag>.txt with its own ledger (e.g. m89: covers on the
# first 89 odd primes, about 2e7 members a vector); kmax is then set per vector so that N stays below 10^200.
#
# Needs starts/q<Q>.txt (good covers to walk from; specs_to_covers.py makes one from any spec file).  The vectors
# handed out so far are remembered in starts/ledger_q<Q>.txt and never repeated; use a new seed for every batch.
# The result is rechecked by check_specs.py before the script reports success.
set -e
cd "$(dirname "$0")"
Q=$1; KCAP=$2; COUNT=$3; NAME=$4; SEED=${5:-1}; TAG=$6
[ -n "$NAME" ] || { echo "usage: $0 Q kcap count name [seed] [tag]" >&2; exit 1; }
[ -x ./covergen ] || gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm
SUF=${TAG:+_$TAG}; KMAX=5.4e9; [ -n "$TAG" ] && KMAX=auto
[ -n "$GEN_KMAX" ] && KMAX=$GEN_KMAX      # e.g. GEN_KMAX=top32: 32-bit k ranges that end at 10^200 (see make_specs.py)
START=starts/q$Q$SUF.txt; LEDGER=starts/ledger_q$Q$SUF.txt; OUT=specs_q${Q}${SUF}_$NAME.json
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
# the walk is asked for more than count: some of what it finds was handed out before
./covergen "$Q" "$START" "$KCAP" $((COUNT * 3 + 2000)) "$SEED" > "$TMP"
cat "$START" >> "$TMP"
python3 make_specs.py "$Q" "q${Q}${SUF}_$NAME" "$KMAX" "$TMP" "$OUT" "$COUNT" "$KCAP" "$LEDGER"
python3 check_specs.py "$OUT"

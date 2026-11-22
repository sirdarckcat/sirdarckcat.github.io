#!/bin/sh
# Search vectors in bulk: count new specs for target Q with at most kcap uncovered rows, best first.
#
#   ./gen_vectors.sh Q kcap count name [seed]      ->  specs_q<Q>_<name>.json
#
# Needs starts/q<Q>.txt (good covers to walk from; specs_to_covers.py makes one from any spec file).  The vectors
# handed out so far are remembered in starts/ledger_q<Q>.txt and never repeated; use a new seed for every batch.
# The result is rechecked by check_specs.py before the script reports success.
set -e
cd "$(dirname "$0")"
Q=$1; KCAP=$2; COUNT=$3; NAME=$4; SEED=${5:-1}
[ -n "$NAME" ] || { echo "usage: $0 Q kcap count name [seed]" >&2; exit 1; }
[ -x ./covergen ] || gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm
START=starts/q$Q.txt; LEDGER=starts/ledger_q$Q.txt; OUT=specs_q${Q}_$NAME.json
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
# the walk is asked for more than count: some of what it finds was handed out before
./covergen "$Q" "$START" "$KCAP" $((COUNT * 3 + 2000)) "$SEED" > "$TMP"
cat "$START" >> "$TMP"
python3 make_specs.py "$Q" "q${Q}_$NAME" 5.4e9 "$TMP" "$OUT" "$COUNT" "$KCAP" "$LEDGER"
python3 check_specs.py "$OUT"

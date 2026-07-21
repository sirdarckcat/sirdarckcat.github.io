#!/bin/bash
# usage: supervise.sh TAG TLO_DEFAULT MAXLOOPS "full tsearch2 args except --t-lo"
TAG=$1; TLO=$2; LOOPS=$3; shift 3
for i in $(seq 1 $LOOPS); do
  if [ -f ${TAG}_hits.json ] && grep -q '"q": [0-9]' ${TAG}_hits.json 2>/dev/null; then
    echo "[supervisor] hit already recorded; exiting"; exit 0
  fi
  LAST=$(grep -o 't~[0-9]*' log_${TAG}_search.txt 2>/dev/null | tail -1 | cut -c3-)
  [ -n "$LAST" ] && [ "$LAST" -gt "$TLO" ] && TLO=$LAST
  echo "[supervisor] round $i starting at t=$TLO" >> log_${TAG}_search.txt
  python3 tsearch2.py --t-lo $TLO "$@" --out ${TAG}_hits.json >> log_${TAG}_search.txt 2>&1
  if grep -q '"q": [0-9]' ${TAG}_hits.json 2>/dev/null; then
    echo "[supervisor] SUCCESS" >> log_${TAG}_search.txt; exit 0
  fi
  grep -q "search done" <(tail -n 2 log_${TAG}_search.txt) && exit 0
  sleep 5
done

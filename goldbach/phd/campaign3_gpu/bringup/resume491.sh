#!/bin/bash
# On a card that replaces a 491-family RTX card (its snapshot restored c170r's search.log, cover491's ledger_p<P>.txt, vecgen491.log and rowguard491_base.txt): the old card's
# unconsumed chunks are not in the snapshot, so the generator restarts with nothing ahead (vec491/made.txt = the vectors consumed) and numbers its chunks after every chunk the
# old card made (vec491/seq0.txt), so no vector name is reused and the campaign's done set (keyed by name) skips nothing new. Their covers stay in the ledger (never made twice).
#   bash resume491.sh PART     (one line on stdout; nothing is done on a card without a restored c170r/search.log, or with chunks already in vec491)
PART=${1:?}
mkdir -p /content/vec491 /content/c170r
if [ -s /content/c170r/search.log ] && ! ls /content/vec491/vec_*.json > /dev/null 2>&1; then
  used=$(grep -c '^\[q170000_m89r491' /content/c170r/search.log)
  s0=$(grep -o '^[0-9T:-]*Z chunk [0-9]*:' /content/vecgen491.log 2>/dev/null | awk '{print $3}' | tr -d : | sort -n | tail -n 1)
  s1=$(grep -o '^\[q170000_m89r491_p[0-9]*c[0-9]*' /content/c170r/search.log | sed 's/.*c0*\([0-9][0-9]*\)$/\1/' | sort -n | tail -n 1)
  seq0=$(( $(printf '%s\n%s\n' "${s0:--1}" "${s1:--1}" | sort -n | tail -n 1) + 1 ))
  echo "$used" > /content/vec491/made.txt; echo "$seq0" > /content/vec491/seq0.txt
  echo "$(date -u +%FT%TZ) resume: c170r done set $(grep -c '^\[' /content/c170r/search.log) slices ($used 491 vectors consumed), chunks continue at $seq0 (old log $s0, search.log $s1), ledger_p$PART $(wc -l < /content/cover491/ledger_p$PART.txt 2>/dev/null) covers, row-guard base $(cat /content/rowguard491_base.txt 2>/dev/null | cut -c1-40)"
else
  echo "$(date -u +%FT%TZ) resume: nothing to resume (fresh c170r or chunks present)"
fi

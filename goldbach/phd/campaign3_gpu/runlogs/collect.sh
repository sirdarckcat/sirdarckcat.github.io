#!/bin/bash
# Collect the per-hour calibration lines of the G4s (calib_peek.py on each card) into OUT (JSON lines, a header object first).   bash collect.sh OUT CARD...
export PATH="$HOME/.local/bin:$PATH"; SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
OUT=${1:?out}; shift; T=$(mktemp)
echo '{"header": true, "keys": ["card", "hour_start", "T", "batches", "windows", "members_scanned", "kept_tested", "expected_near", "expected_design", "found", "events", "down_s", "partial"], "note": "one object an hour per RTX card from its own gpu3_stats.log, found.jsonl and near_events.jsonl; T = the --near-miss in force; expected_near = sum over the batches of (1 - p^)^c at T; events = the verified events written in the hour ({g, N, name, k, sub_record}); down_s = gaps over 30 s between batch lines (downtime or restart); partial = the hour is not wholly covered (drop it from both expectation and count); a card replaced at its 24 h end resumes the same campaign directory, so its lines continue under the new card name", "made": "'$(date -u +%FT%TZ)'"}' > $T
for c in "$@"; do
  timeout 300 colab exec -s $c -f $SP/calib/calib_peek.py --timeout 250 < /dev/null 2>&1 | grep "^\[cal\]" | cut -c7- | python3 -c "
import json, sys
for l in sys.stdin:
    o = json.loads(l); o['host'] = o.pop('card'); o['card'] = '$c'; print(json.dumps(o))" >> $T
done
mv $T $OUT; wc -l $OUT

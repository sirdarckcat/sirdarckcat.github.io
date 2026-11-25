#!/bin/bash
# Collect the per-hour calibration lines of the G4s (calib_peek.py on each card) into OUT (JSON lines, a header object first).   bash collect.sh OUT CARD...
export PATH="$HOME/.local/bin:$PATH"; SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
OUT=${1:?out}; shift; T=$(mktemp)
echo '{"header": true, "version": 2, "keys": ["card", "host", "hour_start", "T", "batches", "windows", "members_scanned", "kept_tested", "tests_counted", "keep_batches", "expected_near", "expected_design", "found", "events", "unmatched", "down_s", "gaps", "partial"], "note": "one object per hour and near-miss threshold T per RTX card (calib_peek.py v2), from the card'"'"'s own gpu3_stats.log, found.jsonl and near_events.jsonl, batch lines from 19:55Z on 25 Nov. T = the --near-miss in force; an hour in which T changed is split into one object per T, each partial. kept_tested = the kept members Fermat-tested (per batch 125,952 a 2^24 window at keep 0.75%, 251,904 at 1.5%: 512 selection blocks x ceil(2^15 (1 - f)); the keep is told by the mean tests a window of each run of batch lines between restarts). tests_counted = the batch lines'"'"' tests counted. expected_near = sum over the batches of the logged expected near>=T; expected_design = sum of the logged expected hits (g >= Q = 170,000). events = the verified events the hour'"'"'s batches wrote ({g, N, name, k, sub_record, t}), matched to the writing batch by vector name; unmatched = found counts no event matched. down_s = gaps over 30 s between batch lines; gaps = [time, s] of every gap over 5 s (restarts, pauses; below 30 s, so not in down_s). partial = the object does not cover its whole hour (drop it from both expectation and count). A card replaced at its 24 h end resumes the same campaign directory, so its lines continue under the new card name. v1 (23:05Z) had kept_tested at the 1.5% keep for every batch and one object an hour.", "made": "'$(date -u +%FT%TZ)'"}' > $T
for c in "$@"; do
  timeout 300 colab exec -s $c -f $SP/calib/calib_peek.py --timeout 250 < /dev/null 2>&1 | grep "^\[cal\]" | cut -c7- | python3 -c "
import json, sys
for l in sys.stdin:
    o = json.loads(l); o['host'] = o.pop('card'); o['card'] = '$c'; print(json.dumps(o))" >> $T
done
mv $T $OUT; wc -l $OUT

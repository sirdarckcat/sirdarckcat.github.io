#!/bin/bash
# gold-g4f -> gold-g4i: the proactive handover at 19:59Z stopped and snapshotted gold-g4f, but Colab refused a new G4 (412 Precondition Failed) for 21 min.
# Retry with handover.sh (the old card is gone and its final snapshot is local, so it goes straight to creating the session): up to 5 rounds of its 40 tries.
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
for round in 1 2 3 4 5; do
  echo "$(date -u +%T) round $round"
  bash $SP/bringup/handover.sh gold-g4f gold-g4i G4 rtx491 2 2026-11-24T19:59:00Z 2>&1 | grep -v Uploaded
  ls $SP/bringup/launch_bu_gold-g4i.py > /dev/null 2>&1 && grep -q '' /dev/null
  export PATH="$HOME/.local/bin:$PATH"
  timeout 90 colab sessions < /dev/null 2>&1 | grep -q '^\[gold-g4i\]' && { echo "$(date -u +%T) gold-g4i exists: done"; exit 0; }
  sleep 60
done
echo "RETRY-G4I-GAVE-UP after 5 rounds"

#!/bin/bash
# Hand a card over to its replacement when Colab's 24 h limit ends it (the user approved replacements, 23 Nov ~20:10Z):
# wait for its final snapshot (the snapshot job) and for the old session to leave `colab sessions` (or a deadline), create the new session (retry while Colab refuses the
# allocation), upload the old card's final snapshot and the bring-up kit, launch the bring-up. One line a step on stdout.
#   bash handover.sh OLD NEW GPU KIND PART DEADLINE_UTC      KIND: rtx491 | l4 ; PART: the RTX generator partition (ignored for l4)
OLD=${1:?}; NEW=${2:?}; GPU=${3:?}; KIND=${4:?}; PART=${5:-0}; DL=${6:?}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
t=$(date -d "$DL" +%s)
until [ -s "$SP/snap/$OLD/final_snap.tgz" ] || [ "$(date +%s)" -ge "$t" ]; do sleep 20; done
echo "$(date -u +%T) $OLD: final snapshot $(ls -la "$SP/snap/$OLD/final_snap.tgz" 2>/dev/null | awk '{print $5}')"
until ! c 90 sessions | grep -q "^\[$OLD\]" || [ "$(date +%s)" -ge $((t + 900)) ]; do sleep 30; done
echo "$(date -u +%T) $OLD: gone from the session list (or deadline + 15 min)"
for i in $(seq 1 40); do
  r=$(c 400 new -s "$NEW" --gpu "$GPU" | tail -n 1)
  echo "$r" | grep -q "READY" && break
  sleep 30
done
echo "$(date -u +%T) $NEW: $r"
echo "$r" | grep -q "READY" || { echo "HANDOVER-FAILED $NEW not created"; exit 1; }
SNAPF="$SP/snap/$OLD/final_snap.tgz"; [ -s "$SNAPF" ] || SNAPF="$SP/snap/$OLD/snap.tgz"
c 300 upload -s "$NEW" "$SNAPF" /content/snap.tgz | tail -n 1 | cut -c1-40
if [ "$KIND" = rtx491 ]; then
  for f in cover491.tgz vecgen491.sh rowguard491.py rowguard491.sh bringup_rtx491.sh kc_top_check.py; do c 120 upload -s "$NEW" "$B/$f" "/content/$f" | tail -n 1 | cut -c1-40; done
  sed "s/PARTX/$PART/" "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
else
  c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$B/bringup_l4.sh" /content/bringup_l4.sh | tail -n 1 | cut -c1-40
  sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
fi
for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
echo "$(date -u +%T) $NEW: bring-up $r"
for k in $(seq 1 40); do
  r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]")
  echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break
  sleep 30
done
echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ') | $(echo "$r" | grep -o 'campaign procs [0-9]* | [^|]*' | tail -n 1 | cut -c1-200)"

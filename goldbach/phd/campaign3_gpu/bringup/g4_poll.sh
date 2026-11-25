#!/bin/bash
# The lead (24 Nov 20:21Z): try for a G4 every ~10 min. When one comes: stop the stopgap L4 at a batch end (snapshot it first: its share's done set is kept), then bring
# partition 2 up on the G4 from gold-g4f's final snapshot (resume: done set, ledger, chunk numbering, row-guard base). One line a step; ends after one success or MAXTRY.
#   bash g4_poll.sh STOPGAP_SESSION [MAXTRY]
STOPGAP=${1:?}; MAXTRY=${2:-11}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup; NEW=gold-g4i; OLD=gold-g4f
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
for t in $(seq 1 $MAXTRY); do
  r=$(c 400 new -s "$NEW" --gpu G4 | tail -n 1)
  echo "$(date -u +%T) try $t: $(echo "$r" | cut -c1-80)"
  echo "$r" | grep -q "READY" && break
  [ $t -lt $MAXTRY ] && sleep 600
done
echo "$r" | grep -q "READY" || { echo "G4-POLL-GAVE-UP after $MAXTRY tries"; exit 2; }
echo "G4-READY $(date -u +%T)"
if c 90 sessions | grep -q "^\[$STOPGAP\]"; then
  mkdir -p "$SP/snap/$STOPGAP"
  r=$(c 200 exec -s "$STOPGAP" -f $B/stop_at_batch.py --timeout 180 | grep "^\[sab\]"); echo "$(date -u +%T) $STOPGAP: $r"
  r=$(c 200 exec -s "$STOPGAP" -f $SP/snap/snap.py --timeout 180 | grep "^\[snap\]"); echo "$(date -u +%T) $STOPGAP: $r"
  c 300 download -s "$STOPGAP" /content/snap.tgz "$SP/snap/$STOPGAP/final_snap.tgz" | tail -n 1 | cut -c1-30
  r=$(c 150 exec -s "$STOPGAP" -f $SP/found/peek_found.py --timeout 120)
  echo "$r" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do grep -qxF "$line" $SP/found/$STOPGAP.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$STOPGAP.jsonl; echo "NEW FOUND LINE on $STOPGAP: ${line:0:300}"; }; done
  [ -s "$SP/snap/$STOPGAP/final_snap.tgz" ] && c 120 stop -s "$STOPGAP" | tail -n 1
  echo "$(date -u +%T) $STOPGAP: stopped (snapshot $(ls -la "$SP/snap/$STOPGAP/final_snap.tgz" 2>/dev/null | awk '{print $5}') bytes)"
fi
c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
for f in cover491.tgz vecgen491.sh rowguard491.py rowguard491.sh bringup_rtx491.sh resume491.sh kc_top_check.py kc_prod.sh; do c 120 upload -s "$NEW" "$B/$f" "/content/$f" | tail -n 1 | cut -c1-40; done
c 120 upload -s "$NEW" "$SP/m89/m89_8.json" /content/m89_8.json | tail -n 1 | cut -c1-40
sed "s/PARTX/2/" "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
echo "$(date -u +%T) $NEW: bring-up $r"
for k in $(seq 1 40); do sleep 30; r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]"); echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break; done
echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ')"

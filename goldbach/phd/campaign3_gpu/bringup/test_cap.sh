#!/bin/bash
# The lead's test (24 Nov 21:14Z): is Colab's cap on sessions (6 in all) or on G4s? (1) stop gold-xt4b at a batch end (snapshot, found lines); (2) with 5 active, try the G4
# for partition 2 (~5 min); (3a) granted: partition 2 resumes on it from gold-g4f's snapshot, the T4 share waits in its snapshot; (3b) refused: recreate the T4 from its
# snapshot at once (resume c170g); if no T4 either, an L4 on the T4's share (the lead approved). One line a step.
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
OLD=gold-xt4b
mkdir -p "$SP/snap/$OLD"
r=$(c 200 exec -s $OLD -f $B/stop_at_batch.py --timeout 180 | grep "^\[sab\]"); echo "$(date -u +%T) $OLD: $r"
r=$(c 200 exec -s $OLD -f $SP/snap/snap.py --timeout 180 | grep "^\[snap\]"); echo "$(date -u +%T) $OLD: $r"
c 300 download -s $OLD /content/snap.tgz "$SP/snap/$OLD/final_snap.tgz" | tail -n 1 | cut -c1-30
r=$(c 150 exec -s $OLD -f $SP/found/peek_found.py --timeout 120)
echo "$r" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do grep -qxF "$line" $SP/found/$OLD.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$OLD.jsonl; echo "NEW FOUND LINE on $OLD: ${line:0:300}"; }; done
[ -s "$SP/snap/$OLD/final_snap.tgz" ] || { echo "TEST-ABORTED: no final snapshot of $OLD (its campaign is stopped: restart it by hand)"; exit 1; }
echo "$(date -u +%T) $OLD: final snapshot $(ls -la "$SP/snap/$OLD/final_snap.tgz" | awk '{print $5}') bytes; stopping the session"
c 120 stop -s $OLD | tail -n 1
sleep 20
G=""
for i in $(seq 1 10); do r=$(c 400 new -s gold-g4i --gpu G4 | tail -n 1); echo "$(date -u +%T) G4 try $i: $(echo "$r" | cut -c1-90)"; echo "$r" | grep -q READY && { G=1; break; }; sleep 30; done
bringup() {   # NEW KIND(rtx491 PART | l4) SNAP
  local NEW=$1 KIND=$2 ARG=$3 SNAP=$4
  c 300 upload -s "$NEW" "$SNAP" /content/snap.tgz | tail -n 1 | cut -c1-40
  if [ "$KIND" = rtx491 ]; then
    for f in cover491.tgz vecgen491.sh rowguard491.py rowguard491.sh bringup_rtx491.sh resume491.sh kc_top_check.py kc_prod.sh; do c 120 upload -s "$NEW" "$B/$f" "/content/$f" | tail -n 1 | cut -c1-40; done
    c 120 upload -s "$NEW" "$SP/m89/m89_8.json" /content/m89_8.json | tail -n 1 | cut -c1-40
    sed "s/PARTX/$ARG/" "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
  else
    c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
    c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
    c 120 upload -s "$NEW" "$SP/l4op/opl4gate2.sh" /content/opl4gate2.sh | tail -n 1 | cut -c1-40
    c 120 upload -s "$NEW" "$B/bringup_l4.sh" /content/bringup_l4.sh | tail -n 1 | cut -c1-40
    sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
  fi
  for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
  echo "$(date -u +%T) $NEW: bring-up $r"
  for k in $(seq 1 40); do sleep 30; r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]"); echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break; done
  echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ')"
}
if [ -n "$G" ]; then
  echo "CAP-TEST: G4 GRANTED with 5 active -> the cap is on sessions; partition 2 resumes on gold-g4i, the T4 share waits in $OLD's snapshot"
  [ -s "$SP/found/gold-g4f.jsonl" ] && cat "$SP/found/gold-g4f.jsonl" >> "$SP/found/gold-g4i.jsonl"
  bringup gold-g4i rtx491 2 "$SP/snap/gold-g4f/final_snap.tgz"
  exit 0
fi
echo "CAP-TEST: G4 REFUSED with 5 active -> the limit is on G4s; recreating the T4"
T=""
for i in $(seq 1 6); do r=$(c 400 new -s gold-xt4c --gpu T4 | tail -n 1); echo "$(date -u +%T) T4 try $i: $(echo "$r" | cut -c1-90)"; echo "$r" | grep -q READY && { T=gold-xt4c; break; }; sleep 30; done
if [ -z "$T" ]; then
  for i in $(seq 1 6); do r=$(c 400 new -s gold-l4x --gpu L4 | tail -n 1); echo "$(date -u +%T) L4 try $i: $(echo "$r" | cut -c1-90)"; echo "$r" | grep -q READY && { T=gold-l4x; break; }; sleep 30; done
fi
[ -n "$T" ] || { echo "CAP-TEST: neither a T4 nor an L4 could be created: the T4 share waits in $OLD's snapshot"; exit 3; }
[ -s "$SP/found/$OLD.jsonl" ] && cat "$SP/found/$OLD.jsonl" >> "$SP/found/$T.jsonl"
bringup $T l4 - "$SP/snap/$OLD/final_snap.tgz"

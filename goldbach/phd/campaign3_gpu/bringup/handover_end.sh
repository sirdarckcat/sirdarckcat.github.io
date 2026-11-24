#!/bin/bash
# The lead's rule (24 Nov 22:46Z, replacing the 23 h stops): keep OLD running to Colab's 24 h end. Snapshot it at T1 (~23 h) and T2 (~23.75 h) without stopping its campaign
# (snap.py; the download replaces final_snap.tgz only when complete), pulling its found lines each time. When Colab has ended OLD (it leaves `colab sessions`), create NEW
# (retry), upload the latest snapshot and the kit, and bring it up resuming OLD's campaign dir. At most ~15 min of OLD's last slices are redone or lost from the done records.
#   bash handover_end.sh OLD NEW GPU KIND ARG T1 T2 END      KIND rtx491: ARG = partition | KIND l4: ARG unused
OLD=${1:?}; NEW=${2:?}; GPU=${3:?}; KIND=${4:?}; ARG=${5:?}; T1=${6:?}; T2=${7:?}; END=${8:?}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
mkdir -p "$SP/snap/$OLD"
pullfound() { local r; r=$(c 150 exec -s "$OLD" -f $SP/found/peek_found.py --timeout 120)
  echo "$r" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do grep -qxF "$line" $SP/found/$OLD.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$OLD.jsonl; echo "NEW FOUND LINE on $OLD: ${line:0:300}"; }; done; }
snapshot() { local r; r=$(c 200 exec -s "$OLD" -f $SP/snap/snap.py --timeout 180 | grep "^\[snap\]"); echo "$(date -u +%T) $OLD: $r"
  rm -f "$SP/snap/$OLD/dl.tmp"; c 300 download -s "$OLD" /content/snap.tgz "$SP/snap/$OLD/dl.tmp" | tail -n 1 | cut -c1-30
  if tar -tzf "$SP/snap/$OLD/dl.tmp" > /dev/null 2>&1; then mv "$SP/snap/$OLD/dl.tmp" "$SP/snap/$OLD/final_snap.tgz"; echo "$(date -u +%T) $OLD: snapshot kept ($(ls -la "$SP/snap/$OLD/final_snap.tgz" | awk '{print $5}') bytes)"; else echo "$(date -u +%T) $OLD: snapshot download incomplete, previous one kept"; fi
  pullfound; }
for T in "$T1" "$T2"; do t=$(date -d "$T" +%s); until [ "$(date +%s)" -ge "$t" ]; do sleep 20; done; snapshot; done
e=$(date -d "$END" +%s)
until ! c 90 sessions | grep -q "^\[$OLD\]"; do [ "$(date +%s)" -ge $((e + 2400)) ] && { echo "HANDOVER-WAIT $OLD still running 40 min after its 24 h mark: not replaced"; exit 1; }; sleep 60; done
echo "$(date -u +%T) $OLD: ended by Colab"
[ -s "$SP/snap/$OLD/final_snap.tgz" ] || { echo "HANDOVER-FAILED no snapshot of $OLD"; exit 1; }
[ -s "$SP/found/$OLD.jsonl" ] && cat "$SP/found/$OLD.jsonl" >> "$SP/found/$NEW.jsonl"
for i in $(seq 1 40); do r=$(c 400 new -s "$NEW" --gpu "$GPU" | tail -n 1); echo "$r" | grep -q "READY" && break; sleep 30; done
echo "$(date -u +%T) $NEW: $(echo "$r" | cut -c1-120)"
echo "$r" | grep -q "READY" || { echo "HANDOVER-FAILED $NEW not created ($GPU): $OLD's share waits in $SP/snap/$OLD/final_snap.tgz"; exit 1; }
c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
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

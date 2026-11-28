#!/bin/bash
# gold-l4e's share (c170g in its final snapshot) waits for an L4 (24 Nov 22:39Z: L4s held at 2). One try every ~10 min; when granted, bring it up with KIND l4 (resume c170g
# through bringup_l4.sh: gate, then deploy_l4op.py with the snapshot's KLO and NEAR_MISS). Ends after one success or MAXTRY.
#   bash l4_poll.sh NEW OLD [MAXTRY]
NEW=${1:?}; OLD=${2:?}; MAXTRY=${3:-11}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
for t in $(seq 1 $MAXTRY); do
  r=$(c 400 new -s "$NEW" --gpu L4 | tail -n 1)
  echo "$(date -u +%T) try $t: $(echo "$r" | cut -c1-80)"
  echo "$r" | grep -q "READY" && break
  [ $t -lt $MAXTRY ] && sleep 600
done
echo "$r" | grep -q "READY" || { echo "L4-POLL-GAVE-UP after $MAXTRY tries"; exit 2; }
echo "L4-READY $(date -u +%T)"
[ -s "$SP/found/$OLD.jsonl" ] && cat "$SP/found/$OLD.jsonl" >> "$SP/found/$NEW.jsonl"
c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/l4op/opl4gate2.sh" /content/opl4gate2.sh | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$B/bringup_l4.sh" /content/bringup_l4.sh | tail -n 1 | cut -c1-40
sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
echo "$(date -u +%T) $NEW: bring-up $r"
for k in $(seq 1 40); do sleep 30; r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]"); echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break; done
echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ')"

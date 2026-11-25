#!/bin/bash
# The lead's stopgap (24 Nov 20:21Z): no G4 for partition 2 by 21:00Z -> one extra L4 in its normal mode on a fresh shifted family-B share (top5s), until a G4 comes.
#   bash stopgap_l4.sh NEW SHARE TEMPLATE_SNAP      (TEMPLATE_SNAP: an L4's snapshot with the current env: KLO 32 levels, NEAR_MISS 160357)
NEW=${1:?}; SHARE=${2:?}; TPL=${3:?}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
for i in $(seq 1 20); do r=$(c 400 new -s "$NEW" --gpu L4 | tail -n 1); echo "$r" | grep -q "READY" && break; sleep 30; done
echo "$(date -u +%T) $NEW: $r"; echo "$r" | grep -q "READY" || { echo "STOPGAP-FAILED $NEW not created"; exit 1; }
c 300 upload -s "$NEW" "$TPL" /content/snap.tgz | tail -n 1 | cut -c1-40
c 300 upload -s "$NEW" "$SHARE" /content/m88f_gpu_share.json | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$SP/l4op/opl4gate2.sh" /content/opl4gate2.sh | tail -n 1 | cut -c1-40
c 120 upload -s "$NEW" "$B/bringup_l4new.sh" /content/bringup_l4new.sh | tail -n 1 | cut -c1-40
sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4new.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
echo "$(date -u +%T) $NEW: bring-up $r"
for k in $(seq 1 40); do sleep 30; r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]"); echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break; done
echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ')"

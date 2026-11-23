#!/bin/bash
# Proactive replacement at ~23 h (the lead, 23 Nov 19:27Z; the user approved replacements ~20:10Z): at time AT, wait for a batch end on OLD, snapshot it (snap.py) and download,
# stop its campaign, pull its found lines a last time, stop the OLD session (frees the accelerator slot), create NEW, upload, bring up. One line a step on stdout.
#   bash handover_pro.sh OLD NEW GPU KIND ARG AT_UTC
#     KIND rtx491: ARG = the generator partition (bringup_rtx491.sh; a 491 card's c170r, ledger and chunk numbering go on: resume491.sh);
#     KIND l4: ARG unused, the old card's campaign dir (c170f or c170g) resumes with its done set (bringup_l4.sh);  KIND l4new: ARG = a local share file (fresh campaign dir c170g, bringup_l4new.sh)
OLD=${1:?}; NEW=${2:?}; GPU=${3:?}; KIND=${4:?}; ARG=${5:?}; AT=${6:?}
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup
export PATH="$HOME/.local/bin:$PATH"
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
t=$(date -d "$AT" +%s); until [ "$(date +%s)" -ge "$t" ]; do sleep 20; done
cat > $B/stop_at_batch.py <<'PY'
import glob, os, time
pr = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
d = pr.split("--campaign ")[1].split()[0] if "--campaign " in pr else None
if d:
    st = d + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st)) if os.path.exists(st) else 0
    for _ in range(600):
        if os.path.exists(st) and sum(1 for _ in open(st)) > n0:
            break
        time.sleep(0.05)
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; pkill -f 'vecgen[0-9]*[.]sh'; pkill -f 'rowguard[0-9]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign '")
time.sleep(5)
print("[sab] stopped", d, "| left:", os.popen("pgrep -fc 'search_gpu5[.]py'").read().strip())
PY
mkdir -p "$SP/snap/$OLD"
r=$(c 200 exec -s "$OLD" -f $B/stop_at_batch.py --timeout 180 | grep "^\[sab\]"); echo "$(date -u +%T) $OLD: $r"
r=$(c 200 exec -s "$OLD" -f $SP/snap/snap.py --timeout 180 | grep "^\[snap\]"); echo "$(date -u +%T) $OLD: $r"
c 300 download -s "$OLD" /content/snap.tgz "$SP/snap/$OLD/final_snap.tgz" | tail -n 1 | cut -c1-30
r=$(c 150 exec -s "$OLD" -f $SP/found/peek_found.py --timeout 120)
echo "$r" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do grep -qxF "$line" $SP/found/$OLD.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$OLD.jsonl; echo "NEW FOUND LINE on $OLD: ${line:0:300}"; }; done
[ -s "$SP/snap/$OLD/final_snap.tgz" ] || { echo "HANDOVER-FAILED no final snapshot of $OLD; $OLD left as it is"; exit 1; }
echo "$(date -u +%T) $OLD: final snapshot $(ls -la "$SP/snap/$OLD/final_snap.tgz" | awk '{print $5}') bytes; stopping the session"
c 120 stop -s "$OLD" | tail -n 2
for i in $(seq 1 40); do
  r=$(c 400 new -s "$NEW" --gpu "$GPU" | tail -n 1)
  echo "$r" | grep -q "READY" && break
  sleep 30
done
echo "$(date -u +%T) $NEW: $r"
echo "$r" | grep -q "READY" || { echo "HANDOVER-FAILED $NEW not created ($GPU)"; exit 1; }
# the old card's found lines come back with its snapshot: keep them as already copied for the new card (the watcher prints only lines it has not seen)
[ -s "$SP/found/$OLD.jsonl" ] && cat "$SP/found/$OLD.jsonl" >> "$SP/found/$NEW.jsonl"
if [ "$KIND" = rtx491 ]; then
  c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
  for f in cover491.tgz vecgen491.sh rowguard491.py rowguard491.sh bringup_rtx491.sh resume491.sh kc_top_check.py kc_prod.sh; do c 120 upload -s "$NEW" "$B/$f" "/content/$f" | tail -n 1 | cut -c1-40; done
  c 120 upload -s "$NEW" "$SP/m89/m89_8.json" /content/m89_8.json | tail -n 1 | cut -c1-40
  sed "s/PARTX/$ARG/" "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
elif [ "$KIND" = l4 ]; then        # resume the old card's campaign dir (c170f or c170g) with its done set and share (bringup_l4.sh); ARG unused
  c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$B/bringup_l4.sh" /content/bringup_l4.sh | tail -n 1 | cut -c1-40
  sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
else
  c 300 upload -s "$NEW" "$SP/snap/$OLD/final_snap.tgz" /content/snap.tgz | tail -n 1 | cut -c1-40
  c 300 upload -s "$NEW" "$ARG" /content/m88f_gpu_share.json | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$SP/ua10b/ua10b_cuda.tgz" /content/ua10_cuda.tgz | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$SP/m88f/kc/kc_spec_m88f.json" /content/kc_m88f.json | tail -n 1 | cut -c1-40
  c 120 upload -s "$NEW" "$B/bringup_l4new.sh" /content/bringup_l4new.sh | tail -n 1 | cut -c1-40
  sed 's#bash /content/bringup_rtx491.sh PARTX#bash /content/bringup_l4new.sh#' "$B/launch_bu.py" > "$B/launch_bu_$NEW.py"
fi
for k in 1 2 3 4; do r=$(c 110 exec -s "$NEW" -f "$B/launch_bu_$NEW.py" --timeout 60 | grep "^\[bu-launch\]"); [ -n "$r" ] && break; sleep 10; done
echo "$(date -u +%T) $NEW: bring-up $r"
for k in $(seq 1 40); do
  sleep 30
  r=$(c 110 exec -s "$NEW" -f "$B/peek_bu.py" --timeout 60 | grep "^\[bl\]")
  echo "$r" | grep -q "BRINGUP-DONE\|BRINGUP-FAILED" && break
done
echo "$(date -u +%T) $NEW: $(echo "$r" | grep -o 'BRINGUP-[A-Z]*[^|]*' | tail -n 2 | tr '\n' ' ')"

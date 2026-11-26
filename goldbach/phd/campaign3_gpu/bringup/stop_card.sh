#!/bin/bash
# The lead's unit decision (25 Nov 19:38Z): stop an L4/T4 card at a batch end, snapshot it (fresh: its slice count equal to the card's after the stop), pull its found
# lines, and release the runtime; its share then waits in $SP/snap/CARD/final_snap.tgz. One line a step.   bash stop_card.sh CARD
export PATH="$HOME/.local/bin:$PATH"
S=${1:?card}; SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; B=$SP/bringup; D=$SP/snap/$S; mkdir -p $D
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
r=""; for i in 1 2 3; do r=$(c 200 exec -s $S -f $B/stop_at_batch.py --timeout 180 | grep "^\[sab\]"); [ -n "$r" ] && break; sleep 20; done
echo "$(date -u +%T) $S: ${r:-stop_at_batch gave no line}"; [ -n "$r" ] || { echo "STOPCARD-FAILED $S: not stopped"; exit 1; }
n=""; for i in 1 2 3; do n=$(c 120 exec -s $S -f $B/cnt_c170g.py --timeout 100 | grep "^\[cnt\]"); [ -n "$n" ] && break; sleep 10; done
echo "$(date -u +%T) $S: after the stop $n (slices, campaign procs)"
nc=$(echo "$n" | awk '{print $2}'); [ "$(echo "$n" | awk '{print $3}')" = "0" ] || { echo "STOPCARD-FAILED $S: campaign still running"; exit 1; }
r=""; for i in 1 2 3; do r=$(c 300 exec -s $S -f $SP/snap/snap.py --timeout 280 | grep "^\[snap\]"); [ -n "$r" ] && break; sleep 20; done
echo "$(date -u +%T) $S: ${r:-snap.py gave no line}"; [ -n "$r" ] || { echo "STOPCARD-FAILED $S: no snapshot (card left up, campaign stopped)"; exit 1; }
rm -f $D/dl.tmp; c 400 download -s $S /content/snap.tgz $D/dl.tmp | tail -n 1 | cut -c1-30
if tar -tzf $D/dl.tmp > /dev/null 2>&1 && [ "$(tar -xzOf $D/dl.tmp c170g/search.log | grep -c '^\[')" = "$nc" ]; then
  [ -s $D/final_snap.tgz ] && mv $D/final_snap.tgz $D/final_snap_prev.tgz; mv $D/dl.tmp $D/final_snap.tgz
  echo "$(date -u +%T) $S: snapshot fresh ($nc slices, $(ls -la $D/final_snap.tgz | awk '{print $5}') bytes, engine $(tar -xzOf $D/final_snap.tgz c3g/search_gpu5.py | sha256sum | cut -c1-12))"
else echo "STOPCARD-FAILED $S: downloaded snapshot not fresh or incomplete (card left up, campaign stopped)"; exit 1; fi
out=$(c 200 exec -s $S -f $SP/colab/peek_v3.py --timeout 150)
if echo "$out" | grep -q "^\[fd-end\]"; then
  echo "$out" | grep "^\[fd\]" | cut -c5- | while IFS= read -r line; do grep -qxF "$line" $SP/found/$S.jsonl 2>/dev/null || { echo "$line" >> $SP/found/$S.jsonl; echo "$(date -u +%T) $S: NEW FOUND LINE ${line:0:200}"; }; done
  echo "$(date -u +%T) $S: found lines pulled ($(echo "$out" | grep -c '^\[fd\]'))"
else echo "$(date -u +%T) $S: found-line pull failed (the snapshot has them)"; fi
c 120 stop -s $S | tail -n 1 | cut -c1-80
sleep 5; c 90 sessions | grep -q "^\[$S\]" && echo "STOPCARD-WARN $S still listed" || echo "$(date -u +%T) $S: released"
echo "STOPCARD-DONE $S"

# Watch campaign3 v3 on the five GPUs (gold-gpu L4, gold-g4 and gold-g4b RTX PRO 6000), campaign3 on the CPU runtimes and
# here, the last fscan class-198 slices, and the uarch selftests. Emits a line on a success, a found.jsonl, a
# driver event (C3GPU-, Traceback), a stall, an unreachable runtime, a slice end, or a selftest finishing.
# State in files, so it survives Monitor re-arms.
export PATH="$HOME/.local/bin:$PATH"
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
D=$SP/fjwatch2; mkdir -p $D
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  # GPUs: v3 campaign mode
  for s in $(cat $SP/colab/cards.txt); do
    r=$(c 200 exec -s $s -f $SP/colab/peek_v3.py --timeout 150 | grep "^\[v3\]")
    if [ -z "$r" ]; then
      n=$(( $(cat $D/v3.$s.miss 2>/dev/null || echo 0) + 1 )); echo $n > $D/v3.$s.miss
      [ $n -eq 3 ] && echo "$s v3 peek failed three polls in a row"
      continue
    fi
    echo 0 > $D/v3.$s.miss; echo "$r" > $D/v3.$s.last
    ev=$(echo "$r" | sed -e 's/.*| events: //' -e 's/ | found: .*//'); f=${r##*| found: }
    if [ "$ev" != "none" ] && [ "$ev" != "$(cat $D/v3.$s.ev 2>/dev/null)" ]; then echo "$s v3 EVENT: $ev"; echo "$ev" > $D/v3.$s.ev; fi
    if [ "$f" != "none" ] && [ "$f" != "$(cat $D/v3.$s.found 2>/dev/null)" ]; then echo "$s v3 FOUND: $f"; echo "$f" > $D/v3.$s.found; fi
    n=$(echo "$r" | sed -e 's/.*| slices //' -e 's/ |.*//'); last=$(cat $D/v3.$s.n 2>/dev/null || echo 0)
    if echo "$r" | grep -q "| running |"; then
      if [ "$n" -le "$last" ]; then k=$(( $(cat $D/v3.$s.stall 2>/dev/null || echo 0) + 1 )); echo $k > $D/v3.$s.stall; [ $k -eq 2 ] && echo "$s v3 STALLED: $n slices, none new in two polls"; else echo 0 > $D/v3.$s.stall; fi
      rm -f $D/v3.$s.down
    elif [ ! -e $D/v3.$s.down ]; then echo "$s v3 NOT RUNNING: $(echo "$r" | cut -c1-400)"; touch $D/v3.$s.down; fi
    echo $n > $D/v3.$s.n
  done
  # The lead's row-count guard for f = 0.985 on the RTX cards (rowguard.sh): a trip, or a guard loop that is not running
  for s in $(cat $SP/colab/cards_rtx.txt); do
    r=$(c 200 exec -s $s -f $SP/colab/peek_rg.py --timeout 150 | grep "^\[rg\]")
    [ -z "$r" ] && continue
    if ! echo "$r" | grep -q "tripped: no" && [ ! -e $D/rg.$s.trip ]; then echo "$s ROWGUARD TRIPPED: $r"; touch $D/rg.$s.trip; fi
    if echo "$r" | grep -q "^\[rg\] loop 0 " && echo "$r" | grep -q "tripped: no" && [ ! -e $D/rg.$s.dead ]; then echo "$s ROWGUARD NOT RUNNING: $r"; touch $D/rg.$s.dead; fi
  done
  # CPU shares (search_c.py at k >= 2^32) on the G4 hosts and here
  for s in $(cat $SP/colab/cards_cs.txt); do
    r=$(c 200 exec -s $s -f $SP/colab/peek_cs.py --timeout 150 | grep "^\[cs\]")
    [ -z "$r" ] && continue
    ev=$(echo "$r" | sed -e 's/.*| events: //' -e 's/ | found: .*//'); f=${r##*| found: }
    if [ "$ev" != "none" ] && [ "$ev" != "$(cat $D/cs.$s.ev 2>/dev/null)" ]; then echo "$s CPU-share EVENT: $ev"; echo "$ev" > $D/cs.$s.ev; fi
    if [ "$f" != "none" ] && [ "$f" != "$(cat $D/cs.$s.found 2>/dev/null)" ]; then echo "$s CPU-share FOUND: $f"; echo "$f" > $D/cs.$s.found; fi
  done
  HL=$SP/c3hi/goldbach/phd/campaign3_hi150
  he=$(grep -E "SUCCESS|Traceback|Error" $HL/search.log 2>/dev/null | tail -n 2)
  if [ -n "$he" ] && [ "$he" != "$(cat $D/hi.local.ev 2>/dev/null)" ]; then echo "local CPU-share EVENT: $he"; echo "$he" > $D/hi.local.ev; fi
  if [ -s $HL/found.jsonl ] && [ "$(md5sum < $HL/found.jsonl)" != "$(cat $D/hi.local.found 2>/dev/null)" ]; then echo "local CPU-share FOUND: $(tail -c 300 $HL/found.jsonl)"; md5sum < $HL/found.jsonl > $D/hi.local.found; fi
  if grep -q "C3CPU-END" $HL/driver.log 2>/dev/null && [ ! -e $D/hi.local.final ]; then echo "local CPU-share ENDED: $(tail -n 2 $HL/driver.log | tr '
' ' ')"; touch $D/hi.local.final; fi
  # fscan class 198 on the Colab CPU runtimes still on it
  for s in gold-cpu2 gold-cpu5 gold-cpu gold-cpu3 gold-cpu4; do
    [ -e $D/$s.final ] && continue
    r=$(c 200 exec -s $s -f $SP/colab/peek_fjob.py --timeout 150 | grep "^\[fj\]")
    if [ -z "$r" ]; then
      n=$(( $(cat $D/$s.miss 2>/dev/null || echo 0) + 1 )); echo $n > $D/$s.miss
      [ $n -ge 3 ] && { echo "$s UNREACHABLE three polls in a row"; touch $D/$s.final; }
      continue
    fi
    echo 0 > $D/$s.miss; echo "$r" > $D/$s.last
    ev=${r##*| events: }
    if [ "$ev" != "none" ] && [ "$ev" != "$(cat $D/$s.ev 2>/dev/null)" ]; then echo "$s SUCCESS LINE: $ev"; echo "$ev" > $D/$s.ev; fi
    ex=$(echo "$r" | sed -e 's/.*| exits: //' -e 's/ | events: .*//')
    if [ "$ex" != "none" ] && [ "$ex" != "$(cat $D/$s.ex 2>/dev/null)" ]; then echo "$s SLICE ENDED: ${ex##*;; }"; echo "$ex" > $D/$s.ex; fi
    if echo "$r" | grep -qE "FJOB-FAILED|FNEXT-FAILED|FNEXT-STOPPED|FNEXT-ALL-DONE|\[fj\] not running"; then echo "$s ENDED: $(echo "$r" | cut -c1-400)"; touch $D/$s.final; fi
  done
  # CPU campaign3 on the Colab runtimes and here
  for s in gold-cpu2 gold-cpu5 gold-cpu gold-cpu3 gold-cpu4; do
    [ -e $D/c3.$s.final ] && continue
    r=$(c 200 exec -s $s -f $SP/colab/peek_c3cpu.py --timeout 150 | grep "^\[cc\]")
    [ -z "$r" ] && continue
    e=$(echo "$r" | sed -e 's/.*| events: //' -e 's/ | found: .*//'); f=${r##*| found: }
    if [ "$e" != "none" ] && [ "$e" != "$(cat $D/c3.$s.ev 2>/dev/null)" ]; then echo "CPU campaign3 $s EVENT: $e"; echo "$e" > $D/c3.$s.ev; fi
    if [ "$f" != "none" ] && [ ! -e $D/c3.$s.found ]; then echo "CPU campaign3 $s FOUND: $f"; touch $D/c3.$s.found; fi
    if echo "$r" | grep -q "C3CPU-END"; then echo "CPU campaign3 $s ENDED: $(echo "$r" | cut -c1-300)"; touch $D/c3.$s.final; fi
  done
  LC=$SP/c3cpu_local_run/goldbach/phd/campaign3
  le=$(grep -E "SUCCESS|Traceback|Error" $LC/search.log 2>/dev/null | tail -n 2)
  if [ -n "$le" ] && [ "$le" != "$(cat $D/c3.local.ev 2>/dev/null)" ]; then echo "CPU campaign3 local EVENT: $le"; echo "$le" > $D/c3.local.ev; fi
  if [ -s $LC/found.jsonl ] && [ ! -e $D/c3.local.found ]; then echo "CPU campaign3 local FOUND: $(head -c 300 $LC/found.jsonl)"; touch $D/c3.local.found; fi
  if grep -q "C3CPU-END" $LC/driver.log 2>/dev/null && [ ! -e $D/c3.local.final ]; then echo "CPU campaign3 local ENDED: $(tail -n 2 $LC/driver.log | tr '\n' ' ')"; touch $D/c3.local.final; fi
  # uarch selftests (steps 5-8): done
  for s in; do
    [ -e $D/ua.$s.done ] && continue
    r=$(c 200 exec -s $s -f $SP/colab/peek_uarch2.py --timeout 150 | grep "^\[uo\]")
    if echo "$r" | grep -q "^\[uo\] done"; then echo "$s UARCH SELFTEST DONE"; touch $D/ua.$s.done; fi
  done
  sleep 240
done

# 16M fleet watcher v3: one retry before UNREACHABLE (replaces fleet_watch.sh now that the first A100 is gone). The master list is
# local: the A100's 1e11 survivors + its kills + gold-cpu's [1e11, 3e11] kills (kept fresh by
# watch_gpu.sh), merged into one fleet kill list and pushed to every member. Hard timeouts on
# every Colab call; hb_fleet is touched each loop for the alarm.
export PATH="$HOME/.local/bin:$PATH"
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; F=$SP/fleet
P=/home/user/sirdarckcat.github.io/goldbach/proth; RQ=$P/runs/q16045849; R=$RQ/fleet; mkdir -p $R $F
FLEET="gold-cpu2 gold-cpu3 gold-cpu4 gold-cpu5 gold-gpu gold-cpu"
JOINERS="gold-cpu:5:8:/content/q16m_cpu_deepsieve.log"
last=""; n=0
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  touch $SP/colab/hb_fleet
  ok=1
  cp $RQ/survivors_T32768_B100000000000.json $F/q16m_surv.json
  python3 - $F $RQ <<'PY' || ok=0
import json, sys
F, RQ = sys.argv[1:3]; k = set()
for f in ("survivors_T32768_B100000000000.kills.json", "q16m_surv_cpu.kills.json"):
    k.update(map(tuple, json.load(open(f"{RQ}/{f}"))))
json.load(open(f"{F}/q16m_surv.json"))
json.dump(sorted(map(list, k)), open(f"{F}/q16m_surv.fleet.kills.json.new", "w"))
PY
  [ $ok = 1 ] && mv $F/q16m_surv.fleet.kills.json.new $F/q16m_surv.fleet.kills.json
  status=""
  for s in $FLEET; do
    if [ $ok = 1 ]; then
      c 300 upload -s $s $F/q16m_surv.json /content/q16m_surv.json.tmp > /dev/null
      c 300 upload -s $s $F/q16m_surv.fleet.kills.json /content/q16m_surv.fleet.kills.json.tmp > /dev/null
    fi
    st=$(c 150 exec -s $s -f $SP/colab/fleet_rename.py --timeout 60 | grep "^\[fleet\]")
    if [ -z "$st" ]; then sleep 30; st=$(c 150 exec -s $s -f $SP/colab/fleet_rename.py --timeout 60 | grep "^\[fleet\]"); fi
    [ -z "$st" ] && st="[fleet] UNREACHABLE"
    status="$status
$s $st"
    for f in tests hits; do
      if c 300 download -s $s /content/q16m_fleet/$f.jsonl $F/$s.$f.new | grep -q Downloaded; then mv $F/$s.$f.new $R/${s}_$f.jsonl; fi
    done
  done
  for jn in $JOINERS; do
    IFS=: read s j np lg <<< "$jn"
    echo $j > $F/js; echo $np > $F/jp; echo $lg > $F/jl
    c 120 upload -s $s $F/js /content/fleet_slice > /dev/null; c 120 upload -s $s $F/jp /content/fleet_procs > /dev/null
    c 120 upload -s $s $F/jl /content/fleet_sieve_log > /dev/null
    for f in cpu_search.py gpu_search.py gpu_screen.py; do c 120 upload -s $s $P/$f /content/$f > /dev/null; done
    c 120 upload -s $s $SP/colab/q16m_cpu_helper_plus.jsonl /content/q16m_cpu_helper.jsonl > /dev/null
    js=$(c 150 exec -s $s -f $SP/colab/fleet_join.py --timeout 60 | grep "^\[join\]")
    status="$status ($s $js)"
  done
  key=$(echo "$status" | sed -E 's/tests=[0-9]+//; s/updated=\{[^}]*\}//')
  n=$((n+1))
  if [ "$key" != "$last" ] || [ $((n % 3)) = 0 ]; then echo "$(date +%H:%M) $(echo "$status" | tr '\n' ' ')"; last="$key"; fi
  sleep 600
done

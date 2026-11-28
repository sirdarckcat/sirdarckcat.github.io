export PATH="$HOME/.local/bin:$PATH"
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad; F=$SP/fleet
P=/home/user/sirdarckcat.github.io/goldbach/proth; R=$P/runs/q16045849/fleet; mkdir -p $R
FLEET="gold-cpu2 gold-cpu3 gold-cpu4 gold-cpu5"
JOINERS="gold-A100:4:9:/content/q16m_deepsieve.log gold-cpu:5:8:/content/q16m_cpu_deepsieve.log"
last=""; n=0
q() { "$@" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  # 1. newest list and kill lists from the A100 host, merged into one fleet kill list
  ok=1
  for f in q16m_surv.json q16m_surv.kills.json q16m_surv.cpu.kills.json; do
    q colab download -s gold-A100 /content/$f $F/$f.new | grep -q Downloaded && mv $F/$f.new $F/$f || ok=0
  done
  python3 - $F <<'PY' || ok=0
import json, sys
F = sys.argv[1]; k = set()
for f in ("q16m_surv.kills.json", "q16m_surv.cpu.kills.json"):
    k.update(map(tuple, json.load(open(f"{F}/{f}"))))
json.load(open(f"{F}/q16m_surv.json"))
json.dump(sorted(map(list, k)), open(f"{F}/q16m_surv.fleet.kills.json", "w"))
PY
  # 2. push to every fleet member that is not the source, then rename + status
  status=""
  for s in $FLEET $(for jn in $JOINERS; do echo ${jn%%:*}; done | grep -v gold-A100); do
    if [ $ok = 1 ]; then
      q colab upload -s $s $F/q16m_surv.json /content/q16m_surv.json.tmp > /dev/null
      q colab upload -s $s $F/q16m_surv.fleet.kills.json /content/q16m_surv.fleet.kills.json.tmp > /dev/null
    fi
    st=$(q colab exec -s $s -f $SP/colab/fleet_rename.py --timeout 60 | grep "^\[fleet\]")
    [ -z "$st" ] && st="[fleet] UNREACHABLE"
    status="$status
$s $st"
    q colab download -s $s /content/q16m_fleet/tests.jsonl $R/${s}_tests.jsonl > /dev/null
    q colab download -s $s /content/q16m_fleet/hits.jsonl $R/${s}_hits.jsonl > /dev/null
  done
  # 3. joiners: start their fleet search once their sieve is done
  for jn in $JOINERS; do
    IFS=: read s j np lg <<< "$jn"
    echo $j > $F/js; echo $np > $F/jp; echo $lg > $F/jl
    q colab upload -s $s $F/js /content/fleet_slice > /dev/null; q colab upload -s $s $F/jp /content/fleet_procs > /dev/null
    q colab upload -s $s $F/jl /content/fleet_sieve_log > /dev/null
    for f in cpu_search.py gpu_search.py gpu_screen.py; do q colab upload -s $s $P/$f /content/$f > /dev/null; done
    q colab upload -s $s $P/runs/q16045849/colab_cpu_helper_tests.jsonl /content/q16m_cpu_helper.jsonl > /dev/null
    js=$(q colab exec -s $s -f $SP/colab/fleet_join.py --timeout 60 | grep "^\[join\]")
    if [ "$s" = gold-A100 ]; then
      st=$(q colab exec -s $s -f $SP/colab/fleet_rename.py --timeout 60 | grep "^\[fleet\]")
      q colab download -s $s /content/q16m_fleet/tests.jsonl $R/${s}_tests.jsonl > /dev/null
      q colab download -s $s /content/q16m_fleet/hits.jsonl $R/${s}_hits.jsonl > /dev/null
      status="$status
$s $st $js"
    else
      status="$status ($s $js)"
    fi
  done
  key=$(echo "$status" | sed -E 's/tests=[0-9]+//; s/updated=\{[^}]*\}//')
  n=$((n+1))
  if [ "$key" != "$last" ] || [ $((n % 3)) = 0 ]; then echo "$(date +%H:%M) $(echo "$status" | tr '\n' ' ')"; last="$key"; fi
  sleep 600
done

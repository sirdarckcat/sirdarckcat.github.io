# GPU-host watcher (replaces watch_all4.sh). Every Colab call has a hard timeout, and each loop
# touches hb_gpu so the alarm notices a stall. Logs status lines when they change.
export PATH="$HOME/.local/bin:$PATH"; last=""; relayed=""; G=gold-gpu
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
RUNS=/home/user/sirdarckcat.github.io/goldbach/proth/runs
declare -A LOCAL=([q1e7]=$RUNS/q10000000 [q16m]=$RUNS/q16045849)
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  touch $SP/colab/hb_gpu
  out=$(c 150 exec -s $G -f $SP/colab/status_all.py --timeout 90 | grep -E "^\[")
  [ -z "$out" ] && out="[watch] GPU status call failed (session gone?)"
  cpu=$(c 150 exec -s gold-cpu -f $SP/colab/status_cpu.py --timeout 90 | grep -E "^\[")
  [ -z "$cpu" ] && cpu="[cpu_sieve16m] status call failed (gold-cpu gone?)"
  out="$out
$cpu"
  # relay gold-cpu's kill list to the GPU host when it changes (validated, .tmp + atomic rename)
  if c 150 download -s gold-cpu /content/q16m_surv_cpu.kills.json $SP/colab/cpu_kills.new | grep -q Downloaded && \
     python3 -c "import json,sys; json.load(open(sys.argv[1]))" $SP/colab/cpu_kills.new 2>/dev/null; then
    mv $SP/colab/cpu_kills.new $RUNS/q16045849/q16m_surv_cpu.kills.json
    h=$(sha256sum $RUNS/q16045849/q16m_surv_cpu.kills.json | cut -c1-16)
    if [ "$h" != "$relayed" ]; then
      if c 300 upload -s $G $RUNS/q16045849/q16m_surv_cpu.kills.json /content/q16m_surv.cpu.kills.json.tmp > /dev/null && \
         c 120 exec -s $G -f $SP/colab/relay_rename.py --timeout 60 | grep -q "in place"; then relayed=$h; fi
    fi
  fi
  key=$(echo "$out" | sed -E -e 's/^\[q16m_cpu\] tests=[0-9]+ /[q16m_cpu] /' \
        -e 's/^(\[cpu_sieve16m\]) .*(DONE|Traceback|Error|bad pairs [1-9]|exit|failed).*/\1 \2/' \
        -e 's/^(\[cpu_sieve16m\]) .*(flush|final|started).*(RUNNING|stopped)$/\1 \2 \3/')
  if [ "$key" != "$last" ]; then echo "$(date +%H:%M) $(echo "$out" | tr '\n' ' ')"; last="$key"; fi
  for d in q1e7 q16m; do
    if echo "$out" | grep -q "^\[$d\]"; then
      for f in tests hits; do
        if c 300 download -s $G /content/$d/$f.jsonl $SP/colab/$d.$f.new | grep -q Downloaded; then
          mv $SP/colab/$d.$f.new ${LOCAL[$d]}/gpu_$f.jsonl
        fi
      done
    fi
  done
  echo "$out" | grep -q "QUEUE-DONE" && break
  sleep 180
done

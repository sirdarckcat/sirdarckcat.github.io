export PATH="$HOME/.local/bin:$PATH"; last=""; relayed=""
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
RUNS=/home/user/sirdarckcat.github.io/goldbach/proth/runs
declare -A LOCAL=([q5e6]=$RUNS/q5000000 [q1e7]=$RUNS/q10000000 [q16m]=$RUNS/q16045849)
while true; do
  out=$(colab exec -s gold-A100 -f $SP/colab/status_all.py --timeout 90 < /dev/null 2>&1 | grep -v -i keyring | grep -E "^\[")
  if [ -z "$out" ]; then out="[watch] A100 status call failed (session gone?)"; fi
  cpu=$(colab exec -s gold-cpu -f $SP/colab/status_cpu.py --timeout 90 < /dev/null 2>&1 | grep -v -i keyring | grep -E "^\[")
  if [ -z "$cpu" ]; then cpu="[cpu_sieve16m] status call failed (gold-cpu gone?)"; fi
  out="$out
$cpu"
  # relay gold-cpu's kill list to the A100 host when it changes (upload to .tmp, then atomic rename)
  if colab download -s gold-cpu /content/q16m_surv_cpu.kills.json $RUNS/q16045849/q16m_surv_cpu.kills.json < /dev/null > /dev/null 2>&1; then
    h=$(sha256sum $RUNS/q16045849/q16m_surv_cpu.kills.json | cut -c1-16)
    if [ "$h" != "$relayed" ] && python3 -c "import json,sys; json.load(open(sys.argv[1]))" $RUNS/q16045849/q16m_surv_cpu.kills.json 2>/dev/null; then
      if colab upload -s gold-A100 $RUNS/q16045849/q16m_surv_cpu.kills.json /content/q16m_surv.cpu.kills.json.tmp < /dev/null > /dev/null 2>&1 && \
         colab exec -s gold-A100 -f $SP/colab/relay_rename.py --timeout 60 < /dev/null 2>&1 | grep -q "in place"; then relayed=$h; fi
    fi
  fi
  key=$(echo "$out" | sed -E -e 's/^\[q16m_cpu\] tests=[0-9]+ /[q16m_cpu] /' \
        -e 's/^(\[[a-z0-9_]+deepsieve2?\]) .*(DONE|abandoned|Traceback|Error|bad pairs [1-9]|exit).*/\1 \2/' \
        -e 's/^(\[[a-z0-9_]+deepsieve2?\]) .*(flush|final).*/\1 \2/' \
        -e 's/^(\[cpu_sieve16m\]) .*(DONE|Traceback|Error|bad pairs [1-9]|exit|failed).*/\1 \2/' \
        -e 's/^(\[cpu_sieve16m\]) .*(flush|final|started).*(RUNNING|stopped)$/\1 \2 \3/')
  if [ "$key" != "$last" ]; then echo "$(date +%H:%M) $(echo "$out" | tr '\n' ' ')"; last="$key"; fi
  for d in q5e6 q1e7 q16m; do
    if echo "$out" | grep -q "^\[$d\]"; then
      mkdir -p ${LOCAL[$d]}
      colab download -s gold-A100 /content/$d/tests.jsonl ${LOCAL[$d]}/gpu_tests.jsonl < /dev/null > /dev/null 2>&1 || true
      colab download -s gold-A100 /content/$d/hits.jsonl ${LOCAL[$d]}/gpu_hits.jsonl < /dev/null > /dev/null 2>&1 || true
    fi
  done
  echo "$out" | grep -q "QUEUE-DONE" && break
  sleep 180
done

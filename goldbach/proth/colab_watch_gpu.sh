# GPU-host watcher v2: gold-cpu's sieve is done and its kills are final, so this only watches the
# GPU host. One retry before reporting a failed status call; hard timeouts; heartbeat in hb_gpu.
export PATH="$HOME/.local/bin:$PATH"; last=""; G=gold-gpu
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad
RUNS=/home/user/sirdarckcat.github.io/goldbach/proth/runs
declare -A LOCAL=([q1e7]=$RUNS/q10000000 [q16m]=$RUNS/q16045849)
c() { timeout "$1" colab "${@:2}" < /dev/null 2>&1 | grep -v -i keyring; }
while true; do
  touch $SP/colab/hb_gpu
  out=$(c 150 exec -s $G -f $SP/colab/status_all.py --timeout 90 | grep -E "^\[")
  if [ -z "$out" ]; then sleep 30; out=$(c 150 exec -s $G -f $SP/colab/status_all.py --timeout 90 | grep -E "^\["); fi
  [ -z "$out" ] && out="[watch] GPU status call failed twice (session gone?)"
  key=$(echo "$out" | sed -E -e 's/^\[q16m_cpu\] tests=[0-9]+ /[q16m_cpu] /')
  if [ "$key" != "$last" ]; then echo "$(date +%H:%M) $(echo "$out" | tr '\n' ' ')"; last="$key"; fi
  for d in q16m; do
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

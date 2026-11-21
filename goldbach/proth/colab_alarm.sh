# Exit (and so wake the session) on the first new watcher line that, after removing the
# acknowledged states in alarm_ack.txt (one sed -E regex per line), still needs action;
# or when a watcher loop dies; or when a loop's heartbeat goes stale (a hung Colab call).
SP=/tmp/claude-0/-home-user-sirdarckcat-github-io/c77908ea-3de3-53f8-b6bc-c2f767c11b41/scratchpad/colab
PAT='HIT|NO HIT|UNREACHABLE|failed|Traceback|Error|QUEUE-DONE|1e7 search exited|\[join\] started|bad pairs [1-9]|SIEVE-CHAIN-DONE|DONE:'
a0=$(wc -l < $SP/watch_gpu.log 2>/dev/null || echo 0); f0=$(wc -l < $SP/watch_fleet2.log 2>/dev/null || echo 0)
strip() { local s; s=$(cat); while IFS= read -r re; do [ -n "$re" ] && s=$(printf '%s' "$s" | sed -E "s/$re//g"); done < $SP/alarm_ack.txt; printf '%s\n' "$s"; }
while true; do
  a=$(tail -n +$((a0 + 1)) $SP/watch_gpu.log 2>/dev/null | strip | grep -E "$PAT")
  f=$(tail -n +$((f0 + 1)) $SP/watch_fleet2.log 2>/dev/null | strip | grep -E "$PAT")
  if [ -n "$a$f" ]; then echo "GPU: $a"; echo "FLEET: $f"; exit 0; fi
  if ! pgrep -f "watch_gpu[.]sh" > /dev/null || ! pgrep -f "fleet_watch2[.]sh" > /dev/null; then echo "a watcher loop died"; exit 0; fi
  now=$(date +%s)
  [ $((now - $(stat -c %Y $SP/hb_gpu))) -gt 1200 ] && { echo "GPU watcher stalled"; exit 0; }
  [ $((now - $(stat -c %Y $SP/hb_fleet))) -gt 3600 ] && { echo "fleet watcher stalled"; exit 0; }
  sleep 20
done

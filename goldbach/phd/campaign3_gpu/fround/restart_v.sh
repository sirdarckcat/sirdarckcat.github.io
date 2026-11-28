#!/bin/bash
# Restart this card's vector campaign in place (picks up NEAR_MISS=158209 from /content/next_campaign_env).
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign /content/c170v "
for i in $(seq 1 60); do pgrep -f "search_gpu[345][.]py --campaign /content/c170v " > /dev/null || break; sleep 1; done
setsid nohup bash -c 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" bash /content/run_v5_vec.sh /content/c170v /content/vec89' > /dev/null 2>&1 < /dev/null &
sleep 8; echo "$(date -u +%FT%TZ) restarted | procs $(pgrep -fc 'search_gpu5[.]py --campaign /content/c170v ') | $(grep -o 'NEAR_MISS=[0-9]*' /content/next_campaign_env) | $(cat /content/deep_env_v89)" > /content/restart_v.log

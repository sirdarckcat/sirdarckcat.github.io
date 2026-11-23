#!/bin/bash
# When the campaign in /content/c150 ends (or at once if none runs), install /content/next_specs.json as its my_specs.json
# (the old list kept as my_specs_<time>.json), merge /content/next_env into /content/next_campaign_env, and start
# run_v5_campQ.sh there. The search.log done-set carries over; the new names are new.
while pgrep -f "search_gpu[345][.]py --campaign" > /dev/null; do sleep 20; done
D=$(cat /content/next_campaign_dir)
cp $D/my_specs.json $D/my_specs_$(date -u +%Y%m%dT%H%M%SZ).json
cp /content/next_specs.json $D/my_specs.json
python3 - <<'PY'
d = dict(x.split("=", 1) for x in open("/content/next_campaign_env").read().split())
for x in open("/content/next_env").read().split():
    k, v = x.split("=", 1); d[k] = v
open("/content/next_campaign_env", "w").write(" ".join(f"{k}={v}" for k, v in d.items()))
PY
echo "$(date -u +%FT%TZ) chain_next: $(python3 -c 'import json; s=json.load(open("/content/next_specs.json")); print(len(s), s[0]["name"], "..", s[-1]["name"])') with $(cat /content/next_campaign_env)" >> $D/driver.log
env $(cat /content/next_campaign_env) nohup bash /content/run_v5_campQ.sh $D > /dev/null 2>&1 &

#!/bin/bash
# Switch this runtime's campaign to the deep sieve exactly at a 2^25 boundary: wait until every variant of my_specs.json has
# its 2^20 slice at a row k0 = m * 2^25 in search.log (the campaign runs top down, all variants a row, so [k0, KMAX) is then
# done), stop the campaign, and restart it with KMAX = k0 and DEEP_ARGS (/content/deep_env), so no member is skipped and
# none is scanned twice beyond the batch in flight.  Log: /content/switch_deep.log.
D=$(cat /content/next_campaign_dir); cd $D
python3 - <<'PY'
import json, os, re, time
D = open("/content/next_campaign_dir").read().split()[0]
names = [v["name"] for v in json.load(open(f"{D}/my_specs.json"))]
pat = re.compile(r"^\[(\S+)@(\d+)\] k=\[")
done = {}                       # k0 -> set of names done at that row
off = 0
while True:
    with open(f"{D}/search.log") as f:
        f.seek(off); chunk = f.read(); off = f.tell()
    for l in chunk.splitlines():
        m = pat.match(l)
        if m: done.setdefault(int(m.group(2)), set()).add(m.group(1))
    full = sorted(k for k, s in done.items() if len(s) >= len(names) and k % (1 << 25) == 0 and all(n in s for n in names))
    if full:
        k0 = full[0] if False else min(full)
        # the lowest complete 2^25-aligned row; the rows above it are complete too (top-down)
        open("/content/switch_k0", "w").write(str(k0)); print(time.strftime("%H:%M:%S"), "boundary", k0, flush=True); break
    time.sleep(5)
PY
K0=$(cat /content/switch_k0)
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'; sleep 5
python3 - "$K0" <<'PY'
import sys
k0 = sys.argv[1]
d = dict(x.split("=", 1) for x in open("/content/next_campaign_env").read().split())
d["KMAX"] = k0; d["BATCH"] = "2"; d["SIEVE200"] = "/content/ua57/goldbach/sieve200"
open("/content/next_campaign_env", "w").write(" ".join(f"{k}={v}" for k, v in d.items()))
PY
echo "$(date -u +%FT%TZ) switch_deep: rows >= $K0 done with B = 10^6; deep from KMAX = $K0" >> $D/driver.log
env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh $D > /dev/null 2>&1 &
sleep 5; echo "restarted: $(pgrep -fc 'search_gpu5[.]py --campaign') campaign process(es)"

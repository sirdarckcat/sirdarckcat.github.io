#!/bin/bash
# Replace the single CPU-share driver by 4 drivers x 11 processes on disjoint quarters of the vectors (the engine makes a
# process pool per slice, so one driver keeps at most 32 of 44 processes busy). Old log lines go to the quarter they belong to.
B=/content/c150cpu/goldbach/phd
pkill -f 'cpu_share[.]sh'; pkill -f "cpu_share4_loop_[0-9][.]sh"; sleep 1; pkill -f 'run_campaign3_hi[.]py'; sleep 1; pkill -f 'search_c[.]py'; sleep 2
cp /content/run_campaign3_hi.py $B/campaign3_hi/run_campaign3_hi.py
python3 - <<'PY'
import json, os, re, shutil
B = "/content/c150cpu/goldbach/phd"
specs = json.load(open(B + "/campaign3_hi/specs.json"))
old = open(B + "/campaign3_hi/search.log").read().splitlines() if os.path.exists(B + "/campaign3_hi/search.log") else []
for i in range(4):
    d = f"{B}/campaign3_hi_{i}"; os.makedirs(d, exist_ok=True)
    part = specs[i::4]; names = set(s["name"] for s in part)
    json.dump(part, open(d + "/specs.json", "w"))
    shutil.copy(B + "/campaign3_hi/run_campaign3_hi.py", d + "/run_campaign3_hi.py")
    if not os.path.exists(d + "/search.log"):
        keep = [l for l in old if (m := re.match(r"\[(\S+)@\d+\] k=\[", l)) and m.group(1) in names]
        open(d + "/search.log", "w").write("".join(l + "\n" for l in keep))
    print(i, len(part), "vectors,", len(open(d + "/search.log").read().splitlines()), "old lines")
os.rename(B + "/campaign3_hi/search.log", B + "/campaign3_hi/search.log.split") if os.path.exists(B + "/campaign3_hi/search.log") else None
PY
for i in 0 1 2 3; do
  cat > /content/cpu_share4_loop_$i.sh <<LOOP
cd $B/campaign3_hi_$i
while true; do
  nice -n 5 python3 run_campaign3_hi.py specs.json --chunk-seconds 3600 --procs 11 --batch 8 >> driver.log 2>&1; rc=\$?
  echo "\$(date -u +%FT%TZ) run_campaign3_hi rc=\$rc" >> driver.log
  [ \$rc -ne 0 ] && break
done
echo "C3CPU-END rc=\$rc" >> driver.log
LOOP
  setsid nohup bash /content/cpu_share4_loop_$i.sh > /dev/null 2>&1 < /dev/null &
done
sleep 2; echo "[c4] started: $(pgrep -fc 'run_campaign3_hi[.]py') drivers"

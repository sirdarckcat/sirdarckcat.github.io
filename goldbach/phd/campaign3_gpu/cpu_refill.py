# Refill this host's CPU share (4 drivers of run_campaign3_hi.py in /content/c150cpu/goldbach/phd/campaign3_hi_0..3, k >= 2^32, Q = 150,000) with the
# vectors of /content/cpu_refill.json (a quarter each, specs[i::4]); the old specs.json kept as specs_prev_<n>.json, search.log kept (new names), the loops
# restarted (nice 5, 11 processes each). Only when no driver runs.
import json, os, subprocess, time
B = "/content/c150cpu/goldbach/phd"
if os.popen("pgrep -f 'run_campaign3_hi[.]py'").read().strip():
    raise SystemExit("[cr] a CPU-share driver still runs; nothing changed")
specs = json.load(open("/content/cpu_refill.json"))
for i in range(4):
    d = f"{B}/campaign3_hi_{i}"
    n = 0
    while os.path.exists(f"{d}/specs_prev_{n}.json"):
        n += 1
    os.rename(f"{d}/specs.json", f"{d}/specs_prev_{n}.json")
    json.dump(specs[i::4], open(f"{d}/specs.json", "w"))
    with open(f"{d}/driver.log", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} refill: {len(specs[i::4])} vectors {specs[i]['name']}.. (previous specs in specs_prev_{n}.json)\n")
    subprocess.Popen(f"setsid nohup bash /content/cpu_share4_loop_{i}.sh > /dev/null 2>&1 < /dev/null &", shell=True)
time.sleep(5)
print("[cr] refilled with", len(specs), "vectors:", specs[0]["name"], "..", specs[-1]["name"], "| drivers", os.popen("pgrep -fc 'run_campaign3_hi[.]py'").read().strip(), "| search_c procs", os.popen("pgrep -fc 'search_c[.]py'").read().strip())

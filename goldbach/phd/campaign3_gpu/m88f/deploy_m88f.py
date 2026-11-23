# Research's m88f covers (the first 88 odd primes, b3d6688; 1,257-1,259 rows at Q = 170,000) on this 88-moduli card: the lead's decision of 23 Nov 15:58Z, after the checks
# (m88f_l4.sh, cpu_slice.sh, cpu_brute_k0.py). A new campaign dir /content/c170f with this card's share of the vectors (/content/m88f_share.json) as my_specs.json; the old
# /content/c170 is kept as it is (one restart reverts). The switch waits for a batch to end (a new line in gpu3_stats.log), then restarts run_v5_campQ.sh on /content/c170f.
import json, os, subprocess, time
D = "/content/c170f"; os.makedirs(D, exist_ok=True)
specs = json.load(open("/content/m88f_share.json"))
for s in specs:
    s.pop("kstart", None)
if not os.path.exists(D + "/my_specs.json"):
    json.dump(specs, open(D + "/my_specs.json", "w"))
C = open("/content/next_campaign_dir").read().split()[0]
st = C + "/gpu3_stats.log"
n0 = sum(1 for _ in open(st)) if os.path.exists(st) else 0
for _ in range(240):
    if os.path.exists(st) and sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.25)
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dm] the old campaign did not exit; nothing started")
open("/content/next_campaign_dir", "w").write(D + "\n")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(15)
print("[dm]", time.strftime("%H:%M:%SZ", time.gmtime()), "| from", C, "to", D, "|", len(specs), "vectors | procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {D} '").read().strip())

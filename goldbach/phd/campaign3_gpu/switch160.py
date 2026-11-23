# The move to Q = 160,000 on this runtime: /content/c160/my_specs.json (staged), near-misses at or above the record in hand
# (/content/near_miss_threshold), deep sieve B = 10^8 with a 1,200-row bit matrix; then restart the campaign there.
import os, subprocess, time
thr = open("/content/near_miss_threshold").read().strip() if os.path.exists("/content/near_miss_threshold") else "157837"
assert os.path.getsize("/content/c160/my_specs.json") > 1000000
d = dict(x.split("=", 1) for x in open("/content/next_campaign_env").read().split())
d.update(KLO="1073741824", KMAX="4294967296", SIEVE200="/content/ua57/goldbach/sieve200", NEAR_MISS=thr)
d.setdefault("BATCH", "2")
open("/content/next_campaign_env", "w").write(" ".join(f"{k}={v}" for k, v in d.items()))
open("/content/next_campaign_dir", "w").write("/content/c160")
open("/content/deep_env", "w").write("--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1200")
os.system("pkill -f switch_deep.sh; pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
time.sleep(5)
subprocess.Popen('env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh /content/c160 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[s160]", open("/content/next_campaign_env").read().strip()[:220], "| near-miss", thr, "|", os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read().strip()[-160:])

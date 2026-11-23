# The fixed near-miss driver, the uarch tree at b344e85 (staged large-prime kernel, DEEP_STAGED=1) and a 1,200-row deep bit
# matrix, restarted in place: the campaign's search.log done-set carries over.
import os, subprocess, time
subprocess.run("mkdir -p /content/uaB && cd /content/uaB && tar -xzf /content/uaB.tgz", shell=True)
assert os.path.exists("/content/uaB/goldbach/sieve200/cuda/overlap.py")
thr = open("/content/near_miss_threshold").read().strip() if os.path.exists("/content/near_miss_threshold") else "157837"
d = dict(x.split("=", 1) for x in open("/content/next_campaign_env").read().split())
d.update(SIEVE200="/content/uaB/goldbach/sieve200", DEEP_STAGED="1", NEAR_MISS=thr)
open("/content/next_campaign_env", "w").write(" ".join(f"{k}={v}" for k, v in d.items()))
open("/content/deep_env", "w").write("--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1200")
D = open("/content/next_campaign_dir").read().split()[0]
os.system("pkill -f 'switch_dee[p][.]sh'; pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
time.sleep(5)
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[ds]", D, "|", open("/content/next_campaign_env").read().strip()[-180:], "|", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

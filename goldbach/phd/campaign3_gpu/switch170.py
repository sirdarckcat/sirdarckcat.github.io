# The move to Q = 170,000 on this runtime (lead's decision of 23 Nov 02:53Z): /content/c170/my_specs.json (staged), near-misses at or
# above the record in hand (/content/near_miss_threshold), the staged deep sieve with a 1,300-row bit matrix and the sieve bound and
# p-estimate of /content/s170_env ("SIEVE_B P_EST", default "100000000 0.0715"); then restart the campaign there. The Q = 150,000
# campaign directory is left as it is.
import os, subprocess, time
thr = open("/content/near_miss_threshold").read().strip() if os.path.exists("/content/near_miss_threshold") else "157837"
B, P = (open("/content/s170_env").read().split() + ["100000000", "0.0715"])[:2] if os.path.exists("/content/s170_env") else ("100000000", "0.0715")
assert os.path.getsize("/content/c170/my_specs.json") > 1000000
d = dict(x.split("=", 1) for x in open("/content/next_campaign_env").read().split())
d.update(KLO="1073741824", KMAX="4294967296", SIEVE200="/content/uaB/goldbach/sieve200", DEEP_STAGED="1", NEAR_MISS=thr)
d.setdefault("BATCH", "2")
open("/content/next_campaign_env", "w").write(" ".join(f"{k}={v}" for k, v in d.items()))
open("/content/next_campaign_dir", "w").write("/content/c170")
open("/content/deep_env", "w").write(f"--deep 1 --klog 25 --slice 33554432 --sieve-b {B} --p-est {P} --deep-max-rows 1300")
os.system("pkill -f 'switch_dee[p][.]sh'; pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):                                   # wait until the old process is gone (never two campaigns on one GPU)
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[s170] the old campaign did not exit; nothing started")
subprocess.Popen('env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh /content/c170 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[s170]", open("/content/deep_env").read().strip(), "| near-miss", thr, "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

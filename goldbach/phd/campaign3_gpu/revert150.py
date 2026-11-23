# Back to the Q = 150,000 campaign on this runtime (a small card that cannot hold Q = 170,000): /content/c150, its done-set carries over.
import os, subprocess, time
open("/content/next_campaign_dir", "w").write("/content/c150")
open("/content/deep_env", "w").write("--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1200")
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
subprocess.Popen('env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh /content/c150 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[r150]", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

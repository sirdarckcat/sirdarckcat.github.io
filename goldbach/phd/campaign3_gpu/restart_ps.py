# Add --pool-threads 2 (uarch poolsplit: a pool tested as two halves on two streams) to this runtime's deep arguments and restart the
# campaign in place (its search.log done-set carries over), waiting for the old process to exit first.
import os, subprocess, time
a = open("/content/deep_env").read().strip()
if "--pool-threads" not in a:
    a += " --pool-threads 2"
open("/content/deep_env", "w").write(a)
D = open("/content/next_campaign_dir").read().split()[0]
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[rps] the old campaign did not exit; nothing started")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[rps]", D, "|", open("/content/deep_env").read().strip(), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

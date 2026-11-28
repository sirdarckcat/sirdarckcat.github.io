# A/B phase B on this RTX card: stop the 88-moduli campaign and start the vector campaign (89 moduli, one 2^24 window a vector from its first 200-digit k)
# in /content/c170v from the chunks in /content/vec89 (vecgen.sh), with the production pipeline flags, 4 windows a batch (one flush), pipeline depth 4,
# --log-near-exp 1. Waits for the old process to exit first.
import os, subprocess, time
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[s89] the old campaign did not exit; nothing started")
deep = ("--deep 1 --klog 24 --slice 16777216 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 4 "
        "--trace-pipeline 1 --deep-tile-threads 512 --log-near-exp 1")
open("/content/deep_env_v89", "w").write(deep)
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[s89] started", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip(), "|", deep)

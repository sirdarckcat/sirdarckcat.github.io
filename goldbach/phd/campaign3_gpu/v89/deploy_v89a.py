# A/B phase A on this RTX card: the 88-moduli campaign (/content/c170) with the new driver (search_gpu5_v89.py: --vector-dir, vectorized cq rows,
# --log-near-exp; identical slice lines on 88 moduli) and --log-near-exp 1, so that the expected first-PRP rows >= the record are logged per batch.
# The deployed driver is kept as search_gpu5_prev3.py. Restart in place, waiting for the old process to exit first.
import os, subprocess, time, shutil, hashlib
cur, new, prev3 = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_v89.py", "/content/c3g/search_gpu5_prev3.py"
if not os.path.exists(prev3):
    shutil.copy2(cur, prev3)
shutil.copy2(new, cur)
a = open("/content/deep_env").read().strip()
if "--log-near-exp" not in a:
    a += " --log-near-exp 1"
open("/content/deep_env", "w").write(a)
D = open("/content/next_campaign_dir").read().split()[0]
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dva] the old campaign did not exit; nothing started")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
print("[dva]", D, "| driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "|", a, "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip(), "|", time.strftime("%H:%M:%SZ", time.gmtime()))

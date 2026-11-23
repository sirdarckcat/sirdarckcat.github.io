# Switch this RTX PRO 6000 runtime to the "a2" sieve setting (uarch plt4 / GPU session plt5, 23 Nov: 1.526 / 1.529 s a batch against 1.574 / 1.580 s for the
# deployed pipeline, slice lines identical) and restart the campaign in place (its search.log done-set carries over):
#   tree /content/ua_v3 = a copy of /content/ua_v2 with the uarch 4f8edff sources (GBATCH_GROUP_DELAY_US, tile CTAs of --deep-tile-threads);
#   driver /content/c3g/search_gpu5_xb3.py (the pipeline driver d5e5f14 + search_gpu5_prio.patch, inert by default) as search_gpu5.py (d5e5f14 kept as search_gpu5_prev2.py);
#   GBATCH_GROUP_DELAY_US=500 (a 0.5 ms bubble after each checked row group) and --deep-tile-threads 512. Waits for the old process to exit first.
import os, subprocess, time, shutil, hashlib
T = "/content/ua_v3"
if not os.path.isdir(T):
    subprocess.run(f"cp -a /content/ua_v2 {T}", shell=True, check=True)
subprocess.run(f"tar -xzf /content/ua_v3.tgz -C {T}", shell=True, check=True)
cur, new, prev2 = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_xb3.py", "/content/c3g/search_gpu5_prev2.py"
if not os.path.exists(prev2):
    shutil.copy2(cur, prev2)
shutil.copy2(new, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("SIEVE200=", "GBATCH_GROUP_DELAY_US="))] + [f"SIEVE200={T}/goldbach/sieve200", "GBATCH_GROUP_DELAY_US=500"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env").read().strip()
if "--deep-tile-threads" not in a:
    a += " --deep-tile-threads 512"
open("/content/deep_env", "w").write(a)
D = open("/content/next_campaign_dir").read().split()[0]
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[da2] the old campaign did not exit; nothing started")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
sha = hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12]
print("[da2]", D, "| driver", sha, "| env", [e for e in env if e.startswith(("SIEVE200=", "GBATCH"))], "|", a, "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

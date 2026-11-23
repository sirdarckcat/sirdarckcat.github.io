# Deploy the cross-batch sieve pipeline (uarch a752ea3) on this runtime and restart the campaign in place (its search.log done-set carries over):
#   /content/ua_v2 = a copy of /content/uaB with the a752ea3 sources of sieve200/cuda and fermat661/cuda over it (sync-free sieve windows, overlap.Pipeline);
#   /content/c3g/search_gpu5.py = the patched driver (search_gpu5_xbatch2.patch; defaults = the old behaviour; the old file kept as search_gpu5_prev.py);
#   SIEVE200 -> /content/ua_v2/goldbach/sieve200, GBATCH_DEFER_CHECK=0 (the per-group overflow check: its host round trips let the sieve trickle beside the Fermat
#   rounds; the sync-free window hides nothing at the highest priority, 08:37Z test); deep_env + "--pipeline 1 --pipeline-depth 2 --trace-pipeline 1".
#   Waits for the old process to exit first.
import os, subprocess, time, shutil, hashlib
T = "/content/ua_v2"
if not os.path.isdir(T):
    subprocess.run(f"cp -a /content/uaB {T}", shell=True, check=True)
subprocess.run(f"tar -xzf /content/ua_v2.tgz -C {T}", shell=True, check=True)
cur, new, prev = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_xb2.py", "/content/c3g/search_gpu5_prev.py"
if not os.path.exists(prev):
    shutil.copy2(cur, prev)
shutil.copy2(new, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("SIEVE200=", "GBATCH_DEFER_CHECK="))] + [f"SIEVE200={T}/goldbach/sieve200", "GBATCH_DEFER_CHECK=0"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env").read().strip()
if "--pipeline" not in a:
    a += " --pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
open("/content/deep_env", "w").write(a)
D = open("/content/next_campaign_dir").read().split()[0]
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dpl] the old campaign did not exit; nothing started")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {D} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)
sha = hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12]
print("[dpl]", D, "| driver", sha, "| env", [e for e in env if e.startswith(("SIEVE200=", "GBATCH_DEFER_CHECK="))], "|", a, "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip())

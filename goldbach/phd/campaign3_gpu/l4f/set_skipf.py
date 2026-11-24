# The lead's L4 keep-fraction A/B (23 Nov 16:41Z): this card's campaign (campaign mode, /content/next_campaign_dir) restarts in place at a batch end with SKIPF=F
# in /content/next_campaign_env (the old file kept once as next_campaign_env_pre_skipf). Done set (search.log) carries over. F is set below by the launcher (sed).
import os, shutil, subprocess, time
F = "0.985"
E = "/content/next_campaign_env"
if not os.path.exists(E + "_pre_skipf"):
    shutil.copy2(E, E + "_pre_skipf")
C = open("/content/next_campaign_dir").read().split()[0]
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(600):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
env = [e for e in open(E).read().split() if not e.startswith("SKIPF=")] + [f"SKIPF={F}"]
open(E, "w").write(" ".join(env))
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[sf] the old campaign did not exit; nothing started (env already switched)")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {C} > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(20)
print("[sf]", time.strftime("%H:%M:%SZ", time.gmtime()), "| dir", C, "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(),
      "|", [e for e in env if e.startswith("SKIPF=")], "| start", [l[-120:] for l in open(C + "/driver.log").read().splitlines() if "start search_gpu5" in l][-1:])

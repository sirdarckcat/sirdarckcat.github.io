# The lead's pre-approval (23 Nov): widen KLO to 24-32 levels. 32 levels: KLO = 2^32 - 32 * 2^25 = 3,221,225,472. The campaign goes level by level from the top (--desc),
# so nothing changes before level 16 is done (~26 Nov); then it goes on to levels 17-32 instead of running out. deploy_l4op.py (run at every bring-up) gets the same KLO.
import os, re, subprocess, time
K16, K32 = 3758096384, 3221225472
p = "/content/deploy_l4op.py"; s = open(p).read()
a = "KLO_TOP16 = (1 << 32) - 16 * (1 << 25)"
if a in s:
    open(p + ".tmp", "w").write(s.replace(a, "KLO_TOP16 = (1 << 32) - 32 * (1 << 25)   # widened to 32 levels (the lead's pre-approval of 23 Nov), 24 Nov")); os.replace(p + ".tmp", p)
for f in ("/content/next_campaign_env", "/content/next_campaign_env_deployed"):
    if os.path.exists(f) and f"KLO={K16}" in open(f).read():
        open(f + ".tmp", "w").write(open(f).read().replace(f"KLO={K16}", f"KLO={K32}")); os.replace(f + ".tmp", f)
C = "/content/c170g"
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(1200):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[k32] the old campaign did not exit")
subprocess.Popen(f'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh {C} > /dev/null 2>&1', shell=True, start_new_session=True,
                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(40)
new = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
print("[k32]", time.strftime("%H:%M:%SZ", time.gmtime()), "| klo", re.findall(r"--klo (\d+)", new), "| near-miss", re.findall(r"--near-miss (\d+)", new), "| procs", len(new.splitlines()),
      "| deploy_l4op", "32 levels" if "32 * (1 << 25)" in open(p).read() else "UNCHANGED", "| stats", [l[:110] for l in open(st).read().splitlines()[-1:]])

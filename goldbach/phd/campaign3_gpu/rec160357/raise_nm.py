# The record moved to g = 160,357 (gold-g4d, 24 Nov 17:11Z, certified): report near-misses only at or above it. NEAR_MISS in the env files 158209 -> 160357, then the
# campaign restarts in place at a batch end with its own command (the done set carries over; the generator and the row guard are not touched).
import os, re, subprocess, time
OLD, NEW = "NEAR_MISS=158209", "NEAR_MISS=160357"
for f in ("/content/next_campaign_env", "/content/next_campaign_env_pre_l4op", "/content/next_campaign_env_pre_onepass", "/content/next_campaign_env_deployed", "/content/next_campaign_env_pre_vtop"):
    if os.path.exists(f) and OLD in open(f).read():
        open(f + ".tmp", "w").write(open(f).read().replace(OLD, NEW)); os.replace(f + ".tmp", f)
run = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
C = re.search(r"--campaign (\S+)", run).group(1)
cmd = {"/content/c170r": 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170r /content/vec491',
       "/content/c170g": 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh /content/c170g'}[C]
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
    raise SystemExit("[rnm] the old campaign did not exit")
subprocess.Popen(cmd + " > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(40)
new = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
print("[rnm]", time.strftime("%H:%M:%SZ", time.gmtime()), C, "| near-miss now", re.findall(r"--near-miss (\d+)", new), "| procs", len(new.splitlines()), "| env", [e for e in open("/content/next_campaign_env").read().split() if e.startswith("NEAR_MISS")],
      "| stats", [l[:120] for l in open(st).read().splitlines()[-1:]], "| gen", os.popen("pgrep -fc 'bash /content/vecgen491[.]sh'").read().strip(), "| rg", os.popen("pgrep -fc 'bash /content/rowguard491[.]sh'").read().strip())

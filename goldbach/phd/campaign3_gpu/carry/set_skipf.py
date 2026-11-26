# The lead's item 2 (keep-fraction A/B, 25 Nov 17:57Z): SKIPF in /content/next_campaign_env -> NEW_SKIPF, then the campaign restarts in place at a batch end with its own command
# (done set carries over; generator and row guard untouched). NEW_SKIPF is set below by the caller.
import os, re, subprocess, time
NEW_SKIPF = "@SKIPF@"
ne = open("/content/next_campaign_env").read()
old = re.findall(r"SKIPF=([\d.]+)", ne)
ne = re.sub(r"SKIPF=[\d.]+", "SKIPF=" + NEW_SKIPF, ne)
open("/content/next_campaign_env.tmp", "w").write(ne); os.replace("/content/next_campaign_env.tmp", "/content/next_campaign_env")
C = "/content/c170r"
cmd = 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170r /content/vec491'
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(1200):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
t_stop = time.strftime("%H:%M:%SZ", time.gmtime())
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(90):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[sf] the old campaign did not exit")
subprocess.Popen(cmd + " > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(45)
new = os.popen("pgrep -af 'search_gpu5[.]py --campaign' | grep -v pgrep").read()
print("[sf]", "SKIPF", old, "->", NEW_SKIPF, "| stopped", t_stop, "| restarted", time.strftime("%H:%M:%SZ", time.gmtime()), "| flags", re.findall(r"--(skip-frac [\d.]+|near-miss \d+|record \d+|carry-over \d+)", new),
      "| procs", len(new.splitlines()), "| stats", [l[:170] for l in open(st).read().splitlines()[-1:]], "| gen", os.popen("pgrep -fc 'bash /content/vecgen491[.]sh'").read().strip(),
      "| rg", os.popen("pgrep -fc 'bash /content/rowguard491[.]sh'").read().strip())

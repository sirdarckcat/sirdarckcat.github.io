# Keep fraction f = 0.985 in vector mode on this RTX card: the lead's decision (23 Nov 12:01Z) on vsweep (x1.080 expected near-misses >= 157,837 a second,
# x1.102 design hits a second against f = 0.97, same 24 windows, 29-bit kernel). SKIPF in /content/next_campaign_env; the row-count guard's base is taken first
# (rowguard.py), then the campaign restarts in place (c170v's done-set carries over; the producer keeps running) and the guard loop starts (rowguard.sh).
import os, subprocess, time
os.system("python3 /content/rowguard.py --dry >> /content/rowguard.log 2>&1")
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("SKIPF=")] + ["SKIPF=0.985"]
open("/content/next_campaign_env", "w").write(" ".join(env))
if "--env-only" not in __import__("sys").argv:
    os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
    for _ in range(60):
        if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
            break
        time.sleep(1)
    else:
        raise SystemExit("[df] the old campaign did not exit; nothing started (env already switched: start it by hand)")
    subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                     shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if not os.popen("pgrep -f 'bash /content/rowguard[.]sh'").read().strip():
    subprocess.Popen("nohup bash /content/rowguard.sh > /dev/null 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[df]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "| guard",
      os.popen("pgrep -fc 'bash /content/rowguard[.]sh'").read().strip(), "|", [e for e in env if e.startswith("SKIPF=")], "|", open("/content/rowguard.log").read().splitlines()[-1][:200])

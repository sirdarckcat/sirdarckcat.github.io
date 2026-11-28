# Take the deep head off this RTX card again: the production A/B at f = 0.985 (12:08-12:24Z, ~1,010 batches a card) gave 0.9514 s a batch with the head against 0.9449 s on
# gold-g4 and gold-g4b without it (+0.7%; tests -8.4%, expected near-misses a batch the same). Driver back to search_gpu5_prev5.py (the k29 driver), SIEVE200 back to
# /content/ua_v3, the head flags out of /content/deep_env_v89; SKIPF (0.985) unchanged. Restart in place.
import os, subprocess, time, shutil, hashlib
cur, prev = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_prev5.py"
shutil.copy2(prev, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("SIEVE200=")] + ["SIEVE200=/content/ua_v3/goldbach/sieve200"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env_v89").read().split()
out = []; skip = 0
for i, x in enumerate(a):
    if skip:
        skip -= 1; continue
    if x in ("--deep-head-b", "--deep-head-rows"):
        skip = 1; continue
    out.append(x)
open("/content/deep_env_v89", "w").write(" ".join(out))
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[rh] the old campaign did not exit; nothing started (driver and env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[rh]", time.strftime("%H:%M:%SZ", time.gmtime()), "| driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "| procs",
      os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", [e for e in env if e.startswith(("SIEVE200=", "SKIPF="))], "|", " ".join(out))

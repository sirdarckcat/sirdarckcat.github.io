# Deep head (uarch 0e45ea8) on this RTX card, under the lead's approval with the GPU session's gate. Deploys only if /content/headv/result.txt (headv.sh on this
# card) shows: HEADCHECK-OK (or, with --no-headcheck, the dump gate alone), prod and base slice lines IDENTICAL, DUMPS-IDENTICAL, and the expected near-misses and
# design hits logged with the head within 1% of base. Tree /content/ua_v4 (ua_v3 + 0e45ea8's sieve200/cuda), driver search_gpu5_head.py as search_gpu5.py (the old one
# kept as search_gpu5_prev5.py), --deep-head-b 1000000000 --deep-head-rows 64 in /content/deep_env_v89. Restart in place (the c170v done-set carries over).
import os, re, subprocess, sys, time, shutil, hashlib
R = open("/content/headv/result.txt").read() if os.path.exists("/content/headv/result.txt") else ""
m = re.search(r"head / base: expected near x([\d.]+), expected hits x([\d.]+), tests x([\d.]+)", R)
need_hc = "--no-headcheck" not in sys.argv
ok = ("HEADV-DONE" in R and (not need_hc or "HEADCHECK-OK" in R) and "prod / base slice lines: IDENTICAL" in R and "DUMPS-IDENTICAL" in R and m is not None
      and abs(float(m.group(1)) - 1) <= 0.01 and abs(float(m.group(2)) - 1) <= 0.01 and float(m.group(3)) < 0.97)
if not ok:
    raise SystemExit(f"[dh] gate NOT passed: nothing changed ({m.groups() if m else 'no head/base line'})")
assert os.path.exists("/content/ua_v4/goldbach/sieve200/cuda/ghead.py")
cur, new, prev = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_head.py", "/content/c3g/search_gpu5_prev5.py"
if not os.path.exists(prev):
    shutil.copy2(cur, prev)
shutil.copy2(new, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("SIEVE200=")] + ["SIEVE200=/content/ua_v4/goldbach/sieve200"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env_v89").read().strip()
if "--deep-head-b" not in a:
    a += " --deep-head-b 1000000000 --deep-head-rows 64"
open("/content/deep_env_v89", "w").write(a)
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dh] the old campaign did not exit; nothing started (driver and env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[dh]", time.strftime("%H:%M:%SZ", time.gmtime()), "| driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "| procs",
      os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "| gate", m.groups(), "|", a)

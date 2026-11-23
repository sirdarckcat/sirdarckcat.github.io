# Fused Fermat rounds (--fused-rounds 1, uarch 4639f17) and DEEP_RCTA=8 with --deep-gen-threads 512 on this RTX card, under the lead's standing rule: deploys only if
# /content/comb/result.txt (comb.sh on this card) says COMB-GATE PASSED (24 identical windows in all four runs, the known case's 23 (k, q), comb at least 1% faster).
# Driver search_gpu5_fr.py (k29 + search_gpu5_fround.patch) as search_gpu5.py (the old one kept as search_gpu5_prev6.py), FERMAT28_DIR=/content/f29fr (f29 + fround.py,
# fround_kernels.cuh), DEEP_RCTA=8, --fused-rounds 1 --deep-gen-threads 512 in /content/deep_env_v89. Restart in place (the c170v done-set carries over).
import os, subprocess, time, shutil, hashlib
R = open("/content/comb/result.txt").read() if os.path.exists("/content/comb/result.txt") else ""
if "COMB-GATE PASSED" not in R or "COMB-DONE" not in R:
    raise SystemExit("[dc] gate NOT passed: nothing changed")
assert os.path.exists("/content/f29fr/fround.py") and os.path.exists("/content/f29fr/fround_kernels.cuh")
cur, new, prev = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_fr.py", "/content/c3g/search_gpu5_prev6.py"
if not os.path.exists(prev):
    shutil.copy2(cur, prev)
shutil.copy2(new, cur)
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("FERMAT28_DIR=", "DEEP_RCTA="))] + ["FERMAT28_DIR=/content/f29fr", "DEEP_RCTA=8"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env_v89").read().strip()
for x in ("--fused-rounds 1", "--deep-gen-threads 512"):
    if x.split()[0] not in a:
        a += " " + x
open("/content/deep_env_v89", "w").write(a)
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dc] the old campaign did not exit; nothing started (driver and env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[dc]", time.strftime("%H:%M:%SZ", time.gmtime()), "| driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "| procs",
      os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", [e for e in env if e.startswith(("FERMAT28_DIR=", "DEEP_RCTA=", "SKIPF="))], "|", a)

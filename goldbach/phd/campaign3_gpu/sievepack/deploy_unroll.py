# uarch's generate unroll with clamped loads (0d42e4d) on this RTX card, under the standing rule: deploys only if /content/unrab/result.txt (unrab.sh on this card) says
# UNROLL-GATE PASSED (identical slice lines in all seven runs, the known case's 23 (k, q), the chosen depth >= 1% faster than production). SIEVE200=/content/ua_v7/goldbach/sieve200
# and DEEP_GEN_UNROLL=4 (or 2, whichever ran faster), the six options kept. Restart in place.
import os, re, subprocess, time
R = open("/content/unrab/result.txt").read() if os.path.exists("/content/unrab/result.txt") else ""
if "UNROLL-GATE PASSED" not in R:
    raise SystemExit("[du] gate NOT passed: nothing changed")
best = re.search(r"UNROLL-CHOICE (\w+)", R).group(1)
opts = ["DEEP_GEN_UNROLL=4" if best == "phu" else "DEEP_GEN_UNROLL=2"]
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("SIEVE200=", "DEEP_GEN_UNROLL="))]
env += ["SIEVE200=/content/ua_v7/goldbach/sieve200"] + opts
open("/content/next_campaign_env", "w").write(" ".join(env))
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[du] the old campaign did not exit; nothing started (env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[du]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", best, "|",
      [e for e in env if e.startswith(("SIEVE200=", "DEEP_", "SKIPF=", "NEAR_MISS="))])

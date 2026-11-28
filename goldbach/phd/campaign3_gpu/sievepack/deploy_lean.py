# LEAN (+ the pipelined tile kernel at AT=64) on this RTX card, under the standing rule: deploys only if /content/leanab/result.txt (leanab.sh on this card) says LEAN-GATE PASSED
# (identical slice lines in all seven runs, the known case's 23 (k, q), the chosen set >= 1% faster than production). SIEVE200=/content/ua_v9/goldbach/sieve200 and the chosen set.
# Restart in place.
import os, re, subprocess, time
R = open("/content/leanab/result.txt").read() if os.path.exists("/content/leanab/result.txt") else ""
if "LEAN-GATE PASSED" not in R:
    raise SystemExit("[dl] gate NOT passed: nothing changed")
best = re.search(r"LEAN-CHOICE (\w+)", R).group(1)
lean = ["DEEP_GEN_SCAN2=1", "DEEP_GEN_RESV_LATE=1", "DEEP_GEN_MINRED=1"]
opts = lean + (["DEEP_TILE_PIPE=1", "DEEP_TILE_PIPE_AT=64", "DEEP_TILE_PREFETCH=0"] if best == "phu" else [])
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("SIEVE200=", "DEEP_GEN_SCAN2=", "DEEP_GEN_RESV_LATE=", "DEEP_GEN_MINRED=", "DEEP_TILE_PIPE", "DEEP_TILE_PREFETCH=" if best == "phu" else "@@"))]
env += ["SIEVE200=/content/ua_v9/goldbach/sieve200"] + opts
open("/content/next_campaign_env", "w").write(" ".join(env))
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dl] the old campaign did not exit; nothing started (env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[dl]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", best, "|",
      [e for e in env if e.startswith(("SIEVE200=", "DEEP_", "SKIPF=", "NEAR_MISS="))])

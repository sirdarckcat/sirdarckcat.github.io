# uarch's flat flush and grid order (8558276) on this RTX card, under the standing rule: deploys only if /content/flushab/result.txt (flushab.sh on this card) says FLUSH-GATE
# PASSED (identical slice lines in all seven runs, the known case's 23 (k, q), the chosen combination >= 1% faster than production). SIEVE200=/content/ua_v6/goldbach/sieve200,
# DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256 DEEP_GEN_FLUSH2=1 (and DEEP_GEN_ORDER=1 if that run was the faster). Restart in place.
import os, re, subprocess, time
R = open("/content/flushab/result.txt").read() if os.path.exists("/content/flushab/result.txt") else ""
if "FLUSH-GATE PASSED" not in R:
    raise SystemExit("[df] gate NOT passed: nothing changed")
best = re.search(r"FLUSH-CHOICE (\w+)", R).group(1)
opts = ["DEEP_BIN_PACK=1", "DEEP_GEN_HOIST=1", "DEEP_TILE_UNROLL=4", "DEEP_TILE_PREFETCH=256", "DEEP_GEN_FLUSH2=1"] + (["DEEP_GEN_ORDER=1"] if best == "phup" else [])
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith(("SIEVE200=", "DEEP_BIN_PACK=", "DEEP_GEN_HOIST=", "DEEP_TILE_UNROLL=", "DEEP_TILE_PREFETCH=", "DEEP_GEN_FLUSH2=", "DEEP_GEN_ORDER="))]
env += ["SIEVE200=/content/ua_v6/goldbach/sieve200"] + opts
open("/content/next_campaign_env", "w").write(" ".join(env))
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170v '")
for _ in range(60):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170v '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[df] the old campaign did not exit; nothing started (env already switched: start it by hand)")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[df]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(), "|", best, "|",
      [e for e in env if e.startswith(("SIEVE200=", "DEEP_", "SKIPF=", "NEAR_MISS="))])

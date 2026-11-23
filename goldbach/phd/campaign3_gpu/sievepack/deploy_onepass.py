# uarch's one-pass generate kernel (f1b904a) on this RTX card after its own gate (opgate.sh: slice lines identical on the 24 test vectors, the known case 23/23, >= 1% of a batch):
# SIEVE200 -> /content/ua_v10/goldbach/sieve200 and DEEP_GEN_ONEPASS=1 (+ DEEP_GEN_LB=512,3 when opgate chose "opl") in /content/next_campaign_env (the old file kept once as
# next_campaign_env_pre_onepass); the card's other DEEP_* options unchanged. Restart in place at a batch end (c170v's done set carries over; deep_env_v89 unchanged).
import os, shutil, subprocess, time
E = "/content/next_campaign_env"; C = "/content/c170v"
res = open("/content/opgate/result.txt").read()
if "OP-GATE PASSED" not in res:
    raise SystemExit("[dop] this card's gate did not pass; nothing changed")
ch = open("/content/opgate/choice.txt").read().strip()
add = ["DEEP_GEN_ONEPASS=1"] + (["DEEP_GEN_LB=512,3"] if ch == "opl" else [])
if not os.path.exists(E + "_pre_onepass"):
    shutil.copy2(E, E + "_pre_onepass")
env = [e for e in open(E + "_pre_onepass").read().split() if not e.startswith(("SIEVE200=", "DEEP_GEN_ONEPASS=", "DEEP_GEN_LB="))] + ["SIEVE200=/content/ua_v10/goldbach/sieve200"] + add
st = C + "/gpu3_stats.log"; n0 = sum(1 for _ in open(st))
for _ in range(400):
    if sum(1 for _ in open(st)) > n0:
        break
    time.sleep(0.05)
open(E, "w").write(" ".join(env))
os.system(f"pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign {C} '")
for _ in range(60):
    if not os.popen(f"pgrep -f 'search_gpu[345][.]py --campaign {C} '").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dop] the old campaign did not exit; nothing started (env already switched: start it with restart_v.sh)")
subprocess.Popen(f'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh {C} /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(40)
err = [l[:150] for l in open(C + "/driver.log").read().splitlines()[-40:] if "rror" in l or "Traceback" in l or "static_assert" in l]
print("[dop]", time.strftime("%H:%M:%SZ", time.gmtime()), "| choice", ch, "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {C} '").read().strip(), "| env +", add,
      "| last", [l.split()[0] for l in open(C + "/search.log").read().splitlines()[-2:]], "| errors", err[-2:])

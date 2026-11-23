# Vector campaign on this RTX card: the sieve setting of the 23 Nov 11:12Z vector-mode tune (vplt.sh, r32): no bubble (GBATCH_GROUP_DELAY_US=0) and row groups of 32
# (--deep-rg 32): 1.575 s a batch of 4 vectors against 1.606-1.622 s, slice lines identical, the sieve idle 0.63 s a batch instead of the consumer waiting for it.
# Restart in place (/content/c170v's search.log done-set carries over), waiting for the old process to exit first.
import os, subprocess, time
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("GBATCH_GROUP_DELAY_US=")] + ["GBATCH_GROUP_DELAY_US=0"]
open("/content/next_campaign_env", "w").write(" ".join(env))
a = open("/content/deep_env_v89").read().strip()
if "--deep-rg" not in a:
    a += " --deep-rg 32"
open("/content/deep_env_v89", "w").write(a)
os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign'")
for _ in range(30):
    if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign'").read().strip():
        break
    time.sleep(1)
else:
    raise SystemExit("[dr] the old campaign did not exit; nothing started")
subprocess.Popen('env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" nohup bash /content/run_v5_vec.sh /content/c170v /content/vec89 > /dev/null 2>&1',
                 shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("[dr]", time.strftime("%H:%M:%SZ", time.gmtime()), "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign'").read().strip(), "|", [e for e in env if e.startswith("GBATCH")], "|", a)

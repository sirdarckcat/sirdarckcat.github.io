# The record is now 158,209: report near-misses from there (NEAR_MISS in /content/next_campaign_env; it only changes what is reported). On the 88-moduli cards
# (run_v5_campQ.sh in /content/c170) the campaign restarts in place now; the vector cards pick it up at their next restart.
import os, subprocess, time
env = [e for e in open("/content/next_campaign_env").read().split() if not e.startswith("NEAR_MISS=")] + ["NEAR_MISS=158209"]
open("/content/next_campaign_env", "w").write(" ".join(env))
C = open("/content/next_campaign_dir").read().split()[0]
msg = "env only"
if C == "/content/c170" and os.popen("pgrep -f 'search_gpu5[.]py --campaign /content/c170 '").read().strip():
    os.system("pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f 'search_gpu[345][.]py --campaign /content/c170 '")
    for _ in range(90):
        if not os.popen("pgrep -f 'search_gpu[345][.]py --campaign /content/c170 '").read().strip():
            break
        time.sleep(1)
    subprocess.Popen('env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" nohup bash /content/run_v5_campQ.sh /content/c170 > /dev/null 2>&1',
                     shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10); msg = "restarted, procs " + os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170 '").read().strip()
print("[nm]", time.strftime("%H:%M:%SZ", time.gmtime()), C, "|", [e for e in env if e.startswith("NEAR_MISS=")], "|", msg)

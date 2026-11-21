# Join this host to the 16M fleet once its deep sieve is finished. Args via /content/fleet_slice and /content/fleet_procs.
import os, subprocess
J, NP = open("/content/fleet_slice").read().strip(), open("/content/fleet_procs").read().strip()
log = open("/content/fleet_sieve_log").read().strip()
done = "DONE" in open(log).read() if os.path.exists(log) else False
running = os.popen("pgrep -f 'cpu_search[.]py q16m'").read().strip()
if done and not running and not os.path.exists("/content/q16m_fleet/hits.jsonl"):
    subprocess.Popen(f"cd /content && nohup python3 cpu_search.py q16m_spec.json q16m_surv.json q16m_fleet --procs {NP} "
                     f"--slice {J}/8 --reload 600 --done q16m_cpu_helper.jsonl > q16m_fleet.log 2>&1 &", shell=True, start_new_session=True)
    print(f"[join] started cpu_search slice {J}/8 with {NP} procs")
else:
    print(f"[join] sieve done={done} search running={bool(running)}")

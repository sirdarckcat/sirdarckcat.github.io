import subprocess, sys
J = int(open("/content/fleet_slice").read())
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True)
r = sh("python3 -c 'import gmpy2' 2>/dev/null || pip install -q gmpy2; python3 -c 'import gmpy2; print(\"gmpy2\", gmpy2.version())'; nproc")
print(r.stdout.strip().replace("\n", " "), r.stderr[-200:])
subprocess.Popen(f"cd /content && nohup python3 cpu_search.py q16m_spec.json q16m_surv.json q16m_fleet --procs $(nproc) "
                 f"--slice {J}/8 --reload 600 --done q16m_cpu_helper.jsonl > q16m_fleet.log 2>&1 &", shell=True, start_new_session=True)
import time; time.sleep(20)
print(sh("cat /content/q16m_fleet.log; uptime").stdout)

# Start the 16M fleet slice on the GPU host's spare CPUs; report GPU step rate before and after.
import os, re, subprocess, time
def rate():
    lines = [l for l in open("/content/q1e7/run.log") if "step" in l][-2:]
    (s1, t1), (s2, t2) = [tuple(map(int, re.search(r"step (\d+)/\d+, (\d+)s", l).groups())) for l in lines]
    return (s2 - s1) / max(t2 - t1, 1)
print(f"before: {rate():.1f} steps/s")
if not os.popen("pgrep -f 'cpu_search[.]py q16m'").read().strip():
    subprocess.Popen("cd /content && nohup python3 cpu_search.py q16m_spec.json q16m_surv.json q16m_fleet --procs 9 "
                     "--slice 4/8 --reload 600 --done q16m_cpu_helper.jsonl > q16m_fleet.log 2>&1 &", shell=True, start_new_session=True)
time.sleep(150)
print(f"after:  {rate():.1f} steps/s")
print(subprocess.run("head -n 3 /content/q16m_fleet.log; uptime", shell=True, capture_output=True, text=True).stdout)

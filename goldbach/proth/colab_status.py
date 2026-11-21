import os, subprocess
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
for d in ("q5e6", "q1e7", "q16m"):
    p = f"/content/{d}"
    if not os.path.isdir(p):
        continue
    last = sh(f"grep -E 'batch done|HIT|NO HIT|Error|Traceback|survivors file' {p}/run.log | tail -n 1")
    n = sh(f"wc -l < {p}/tests.jsonl 2>/dev/null") or "0"
    hits = sh(f"cat {p}/hits.jsonl 2>/dev/null").replace("\n", " ")
    print(f"[{d}] tests={n} {('HITFILE ' + hits) if hits else ''} | {last}")
if os.path.isdir("/content/q16m_cpu"):
    n = sh("wc -l < /content/q16m_cpu/tests.jsonl 2>/dev/null") or "0"
    hit = sh("grep -E 'HIT|Traceback|Error' /content/q16m_cpu/run.log | tail -n 1")
    print(f"[q16m_cpu] tests={n} {hit} | helper", "RUNNING" if sh("pgrep -f 'desert[.]py search /content/q16m_spec'") else "stopped")
for name in ("q1e7_deepsieve", "q16m_deepsieve", "q16m_deepsieve2"):
    p = f"/content/{name}.log"
    if os.path.exists(p):
        print(f"[{name}]", sh(f"grep -E 'flush|final|DONE|abandoned|Traceback|Error|bad pairs [1-9]|exit' {p} | tail -n 1") or "started")
print("[queue]", sh("tail -n 1 /content/queue.log"), "| gpu_search", "RUNNING" if sh("pgrep -f 'gpu_search[.]py'") else "idle")

import os, subprocess
# Status of the GPU queue runs on a Colab runtime: python3 colab_status.py (run via colab exec).
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
for d in ("q5e6", "q1e7", "q16m"):
    p = f"/content/{d}"
    if not os.path.isdir(p):
        continue
    last = sh(f"grep -E 'batch done|HIT|NO HIT|Error|Traceback' {p}/run.log | tail -n 1")
    n = sh(f"wc -l < {p}/tests.jsonl 2>/dev/null") or "0"
    hits = sh(f"cat {p}/hits.jsonl 2>/dev/null").replace("\n", " ")
    print(f"[{d}] tests={n} {('HITFILE ' + hits) if hits else ''} | {last}")
print("[queue]", sh("tail -n 1 /content/queue.log"), "| gpu_search", "RUNNING" if sh("pgrep -f gpu_search.py") else "idle")

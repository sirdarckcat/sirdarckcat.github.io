import json, os
n = {}
for f in ("q16m_surv.json", "q16m_surv.fleet.kills.json"):
    t = f"/content/{f}.tmp"
    if os.path.exists(t):
        n[f] = len(json.load(open(t)))          # only complete JSON is moved into place
        os.replace(t, f"/content/{f}")
alive = os.popen("pgrep -f 'cpu_search[.]py q16m' | head -1").read().strip()
tests = sum(1 for _ in open("/content/q16m_fleet/tests.jsonl")) if os.path.exists("/content/q16m_fleet/tests.jsonl") else 0
hit = open("/content/q16m_fleet/hits.jsonl").read().strip() if os.path.exists("/content/q16m_fleet/hits.jsonl") else ""
err = os.popen("grep -E 'Traceback|Error' /content/q16m_fleet.log | tail -n 1").read().strip()
print(f"[fleet] updated={n} tests={tests} search={'RUNNING' if alive else 'stopped'} {('HIT ' + hit) if hit else ''} {err}")

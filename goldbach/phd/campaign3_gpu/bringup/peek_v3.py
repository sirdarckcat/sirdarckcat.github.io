import os, re
run = os.popen("pgrep -af 'search_gpu[345][.]py --campaign' | grep -v pgrep").read().strip()
m = re.search(r"--campaign (\S+)", run)
if m:
    dirs = [m.group(1)]
else:
    cands = [d for d in ("/content/c170r", "/content/c170g", "/content/c170f", "/content/c170v", "/content/c170", "/content/c160", "/content/c150", "/content/c140", "/content/c850", "/content/c3g_g4", "/content/c3g") if os.path.exists(d + "/my_specs.json")]
    dirs = cands[:1]
for d in dirs:
    n, last, succ = 0, "-", []
    if os.path.exists(d + "/search.log"):
        for line in open(d + "/search.log"):
            if line.startswith("["):
                n += 1; last = line.strip()
            elif "SUCCESS" in line or "Traceback" in line or "Error" in line:
                succ.append(line.strip())
    fl = [l for l in open(d + "/found.jsonl").read().splitlines() if l.strip()] if os.path.exists(d + "/found.jsonl") else []
    fnd = f"{len(fl)} lines, last: {fl[-1][:300]}" if fl else ""
    drv = open(d + "/driver.log").read().strip().splitlines() if os.path.exists(d + "/driver.log") else []
    bad = [l for l in drv if "Traceback" in l or "Error" in l or "C3GPU-" in l]
    st = open(d + "/gpu3_stats.log").read().strip().splitlines()[-1:] if os.path.exists(d + "/gpu3_stats.log") else []
    print(f"[v3] {d} | {'running' if m else 'not running'} | slices {n} | last: {last[:170]} | stats: {' '.join(st)[:220]} | driver: {' / '.join(drv[-2:])[-250:]} "
          f"| events: {(' ;; '.join(succ + bad))[:500] or 'none'} | found: {fnd or 'none'}")

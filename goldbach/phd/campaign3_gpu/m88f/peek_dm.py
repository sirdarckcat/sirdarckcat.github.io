import os
if os.path.exists("/content/deploy_m88f.log"):
    print("[pdm]", open("/content/deploy_m88f.log").read()[-800:].strip().replace("\n", " || "))
D = "/content/c170f"
print("[pdm] next", open("/content/next_campaign_dir").read().strip(), "| procs", os.popen(f"pgrep -fc 'search_gpu5[.]py --campaign {D} '").read().strip(),
      "| old procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170 '").read().strip())
if os.path.exists(D + "/driver.log"):
    print("[pdm] driver", " || ".join(l[:260] for l in open(D + "/driver.log").read().splitlines()[-4:]))
for f in ("search.log", "gpu3_stats.log"):
    p = os.path.join(D, f)
    if os.path.exists(p):
        print("[pdm]", f, " || ".join(l[:260] for l in open(p).read().splitlines()[-3:]))

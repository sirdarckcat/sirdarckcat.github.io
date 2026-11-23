import os, hashlib
print("[pdv]", open("/content/deploy_vtop.log").read()[-900:].strip().replace("\n", " || ") if os.path.exists("/content/deploy_vtop.log") else "no log")
print("[pdv] driver", hashlib.sha256(open("/content/c3g/search_gpu5.py", "rb").read()).hexdigest()[:12], "| procs", os.popen("pgrep -fc 'search_gpu5[.]py --campaign /content/c170v '").read().strip(),
      "| start", [l[-60:] for l in open("/content/c170v/driver.log").read().splitlines() if "start search_gpu5" in l][-1:],
      "| last slices", [l.split()[0] for l in open("/content/c170v/search.log").read().splitlines()[-4:]],
      "| errors", [l[:150] for l in open("/content/c170v/driver.log").read().splitlines()[-60:] if "rror" in l or "Traceback" in l or "ssert" in l][-2:])

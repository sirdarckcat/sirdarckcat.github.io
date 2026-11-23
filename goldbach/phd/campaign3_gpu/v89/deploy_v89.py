# Deploy the 89-moduli vector campaign on this RTX card (the lead's gate passed: A/B on gold-g4b 23 Nov, expected near>=record per second x1.605, design hits x1.141):
# the v89 driver becomes /content/c3g/search_gpu5.py (the previous one kept as search_gpu5_prev3.py), then switch_v89b.py stops the 88-moduli campaign and starts the
# vector campaign in /content/c170v from /content/vec89 (vecgen.sh keeps it supplied).
import os, shutil, hashlib
cur, new, prev3 = "/content/c3g/search_gpu5.py", "/content/c3g/search_gpu5_v89.py", "/content/c3g/search_gpu5_prev3.py"
if not os.path.exists(prev3):
    shutil.copy2(cur, prev3)
shutil.copy2(new, cur)
print("[dv] driver", hashlib.sha256(open(cur, "rb").read()).hexdigest()[:12], "| vectors made", open("/content/vec89/made.txt").read().strip() if os.path.exists("/content/vec89/made.txt") else "none", flush=True)
exec(open("/content/switch_v89b.py").read())

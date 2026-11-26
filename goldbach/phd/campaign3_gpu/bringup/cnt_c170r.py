import subprocess
n = sum(1 for l in open("/content/c170r/search.log") if l.startswith("["))
p = subprocess.run(["pgrep", "-fc", "search_gpu5[.]py --campaign"], capture_output=True, text=True).stdout.strip() or "0"
print("[cnt]", n, p)

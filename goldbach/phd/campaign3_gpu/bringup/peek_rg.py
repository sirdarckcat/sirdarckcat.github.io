import os
g = "491" if os.path.exists("/content/rowguard491.sh") else ""
t = open(f"/content/rowguard{g}_tripped.txt").read().strip() if os.path.exists(f"/content/rowguard{g}_tripped.txt") else "no"
last = open(f"/content/rowguard{g}.log").read().strip().splitlines()[-1][:220] if os.path.exists(f"/content/rowguard{g}.log") and open(f"/content/rowguard{g}.log").read().strip() else "no log yet"
print(f"[rg] loop {os.popen('pgrep -fc ' + chr(39) + f'bash /content/rowguard{g}[.]sh' + chr(39)).read().strip()} | tripped: {t} | last: {last}")

# Restart this card's 491 generator on the new vecgen491.sh (the lead's 23 Nov 21:46Z cap-step rules), at an idle moment: no walk, part, make_specs or check_specs
# running, so no ledger line or chunk is cut. The cap continues from the generator's last "cap raised to N" line, CAPMAX 1,252 (the lead's 21:35Z advance decision);
# the chunk numbering continues after the highest chunk in vec491 and made.txt is kept (vecgen491.sh). The campaign is not touched.
import os, re, subprocess, time
assert os.path.exists("/content/vecgen491.sh.new") and "YMIN" in open("/content/vecgen491.sh.new").read()
pr = [l for l in os.popen("pgrep -af 'bash /content/vecgen491[.]sh'").read().splitlines() if "pgrep" not in l]
assert len(pr) == 1, ("expected one running generator", pr)
a = pr[0].split(); V, CAMP, PART, NPART = a[a.index("/content/vecgen491.sh") + 1:][:4]
kids = lambda: [l for l in os.popen("pgrep -af 'covergen 170000|part[.]py walk|make_specs[.]py 170000|check_specs[.]py chunk'").read().splitlines() if "pgrep" not in l]
for _ in range(2400):
    if not kids():
        break
    time.sleep(0.25)
else:
    raise SystemExit("[rgen] the generator never went idle in 10 min; nothing changed")
os.system("pkill -f 'bash /content/vecgen491[.]sh'")
time.sleep(1)
k = kids()
if k:                                                    # a walk that started in that instant (covergen / part.py; make_specs needs the finished walk first)
    assert not [l for l in k if "make_specs" in l or "check_specs" in l], ("make/check running: inspect by hand", k)
    os.system("pkill -f 'covergen 170000'; pkill -f 'part[.]py walk'"); time.sleep(1)
assert not [l for l in os.popen("pgrep -af 'bash /content/vecgen491[.]sh'").read().splitlines() if "pgrep" not in l], "the old generator is still running"
led = f"/content/cover491/ledger_p{PART}.txt"
with open(led, "rb") as f:
    f.seek(-1, 2); assert f.read(1) == b"\n", "the ledger does not end with a newline"
caps = re.findall(r"^cap raised to (\d+)$", open("/content/vecgen491.log").read(), re.M); cap = int(caps[-1]) if caps else 1248
if not os.path.exists("/content/vecgen491.sh.pre2150"):
    os.system("cp /content/vecgen491.sh /content/vecgen491.sh.pre2150")
os.replace("/content/vecgen491.sh.new", "/content/vecgen491.sh")
open("/content/vecgen491.log", "a").write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} generator restarted on the lead's 21:46Z cap-step rules (a walk under 100 new vectors, or under 3,500 ahead after a short walk): CAP={cap} CAPMAX=1252\n")
subprocess.Popen(f"setsid nohup env CAP={cap} CAPMAX=1252 bash /content/vecgen491.sh {V} {CAMP} {PART} {NPART} >> /content/vecgen491.log 2>&1 < /dev/null &", shell=True,
                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
time.sleep(5)
made = open(f"{V}/made.txt").read().split()[0]; used = sum(1 for l in open(f"{CAMP}/search.log") if l.startswith("[q170000_m89r491"))
print("[rgen]", time.strftime("%H:%M:%SZ", time.gmtime()), "| part", PART, "| cap", cap, "| CAPMAX 1252 | gen procs", len([l for l in os.popen("pgrep -af 'bash /content/vecgen491[.]sh'").read().splitlines() if "pgrep" not in l]),
      "| ahead", int(made) - used, "| ledger lines", sum(1 for _ in open(led)), "| log tail", open("/content/vecgen491.log").read().splitlines()[-1][:200])

import re
L = open("/content/vecgen491.log").read().splitlines()
out = []
for l in L:
    m = re.match(r"^(\S+Z) chunk (\d+): (\d+) specs written.*residual sizes (\d+)\.\.(\d+).*?; (\d+) covers skipped.*\| (\d+) s$", l)
    if m:
        out.append(f"{m.group(1)[11:19]} c{m.group(2)} n{m.group(3)} r{m.group(4)}-{m.group(5)} skip{m.group(6)} {m.group(7)}s")
    elif "no chunk" in l or "cap raised" in l:
        out.append(l[:150])
print("[vgl]", " ; ".join(out[:40]))

import os, re
g = "491" if os.path.exists("/content/rowguard491.sh") else ""
t = open(f"/content/rowguard{g}_tripped.txt").read().strip() if os.path.exists(f"/content/rowguard{g}_tripped.txt") else "no"
last = open(f"/content/rowguard{g}.log").read().strip().splitlines()[-1][:220] if os.path.exists(f"/content/rowguard{g}.log") and open(f"/content/rowguard{g}.log").read().strip() else "no log yet"
sup = ""
if g and os.path.exists("/content/vecgen491.log"):       # the 491 generator's supply: current cap, vectors ahead of the campaign, the last chunk's size, stalled at its CAPMAX
    L = open("/content/vecgen491.log").read().splitlines()
    ic = [i for i, l in enumerate(L) if l.startswith("cap raised to ")]; ik = [i for i, l in enumerate(L) if re.match(r"^\S+Z chunk \d+: ", l)]; inc = [i for i, l in enumerate(L) if re.match(r"^\S+Z no chunk at cap ", l)]
    cap = int(L[ic[-1]].split()[-1]) if ic else 1248
    lk = re.match(r"^(\S+Z) chunk (\d+): (\d+) ", L[ik[-1]]) if ik else None
    stall = bool(inc) and inc[-1] > max(ic[-1] if ic else -1, ik[-1] if ik else -1)
    made = int(open("/content/vec491/made.txt").read().split()[0]) if os.path.exists("/content/vec491/made.txt") else 0
    used = sum(1 for l in open("/content/c170r/search.log") if l.startswith("[q170000_m89r491")) if os.path.exists("/content/c170r/search.log") else 0
    sup = f" | sup: cap {cap} | ahead {made - used} | last chunk {('c' + lk.group(2) + ' n' + lk.group(3) + ' at ' + lk.group(1)[11:19]) if lk else 'none'} | stall {'yes: ' + L[inc[-1]][:90] if stall else 'no'} | gen procs {os.popen('pgrep -fc ' + chr(39) + 'bash /content/vecgen491[.]sh' + chr(39)).read().strip()}"
print(f"[rg] loop {os.popen('pgrep -fc ' + chr(39) + f'bash /content/rowguard{g}[.]sh' + chr(39)).read().strip()} | tripped: {t} | last: {last}{sup}")

import re, sys
g = sorted((int(a), int(b)) for a, b in re.findall(r"^GPU k=(\d+) q=(\d+)", open(sys.argv[1]).read(), re.M))
c = sorted((int(a), int(b)) for a, b in re.findall(r"^BRUTE k=(\d+) q=(\d+)", open(sys.argv[2]).read(), re.M))
print(f"GPU {len(g)} | CPU {len(c)} | identical {g == c} | only GPU {sorted(set(g) - set(c))[:5]} | only CPU {sorted(set(c) - set(g))[:5]}")

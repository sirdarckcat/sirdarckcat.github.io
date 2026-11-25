# The stopgap batch top5s (shifted family-B m88f, 24 Nov): every spec is a top32-shifted vector with N in the 200-digit range over 32 levels, residues = its cover, new names.
import json, sys
S = json.load(open(sys.argv[1])); old = set()
for f in sys.argv[2:]:
    old |= {v["name"] for v in json.load(open(f))}
TOP, K32, LO, HI = 1 << 32, (1 << 32) - 32 * (1 << 25), 10 ** 199, 10 ** 200
cv = lambda v: [tuple(map(int, c)) for c in (v["cover"] if isinstance(v["cover"], list) else json.loads(v["cover"]))]
bad = []; names = set()
for v in S:
    N0, M = int(v["N0"]), int(v["M"]); c = cv(v); r = v["residual"] if isinstance(v["residual"], list) else json.loads(v["residual"])
    ok = (v["name"].startswith("q170000_m88f_top5s_v") and v["name"] not in old and v["name"] not in names and int(v["kmax"]) == TOP and int(v["k_shift"]) > 0
          and N0 + (TOP - 1) * M < HI and N0 + TOP * M >= HI and N0 + K32 * M >= LO and len(c) == 88 and all(N0 % p == a for p, a in c) and len(r) <= 1258)
    names.add(v["name"])
    if not ok: bad.append(v["name"])
lo_n = min(int(v["N0"]) + K32 * int(v["M"]) for v in S)
print(f"[t5] {len(S)} specs | bad {len(bad)} {bad[:3]} | N at KLO32 >= {lo_n / 10**199:.3f}e199 | k_shift {min(int(v['k_shift']) for v in S)}..{max(int(v['k_shift']) for v in S)} | distinct from {len(old)} earlier names")
print("[t5] ASSERTS", "PASSED" if not bad else "FAILED")

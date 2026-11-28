"""Residue-swap variants of the Lean session's 850-row cover (spec_q122000_k850.json, ccr-36ca7b46-8twf14 at 3922f8e),
for the range below 10^200: gen_variants.variants(base, 3000, kmax=4294967295, ceiling=200, pair_pool=120)."""
import json, sys, time, collections
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach")
import gen_variants as GV
SP = sys.argv[1]
s = json.load(open(SP + "/c850/spec_q122000_k850.json"))
base = {"Q": int(s["Q"]), "cover": [list(map(int, c)) for c in (json.loads(s["cover"]) if isinstance(s["cover"], str) else s["cover"])],
        "residual": [int(q) for q in (json.loads(s["residual"]) if isinstance(s["residual"], str) else s["residual"])],
        "boost": float(s["boost"]), "m_digits": float(s["m_digits"]), "E": float(s["E"]), "n_digits_est": float(s["n_digits_est"]),
        "N0": str(s["N0"]), "M": str(s["M"]), "name": s["name"], "kmax": 4294967295, "ceiling_digits": 200, "stop_on_success": True}
t0 = time.time()
vs = GV.variants(base, 3000, kmax=4294967295, ceiling=200, pair_pool=120)
for v in vs:
    v["stop_on_success"] = True
allv = [base] + vs
assert len(set(v["N0"] for v in allv)) == len(allv)
json.dump(allv, open(SP + "/c850/specs850.json", "w"))
print(len(allv), "specs;", sorted(collections.Counter(len(v["residual"]) for v in allv).items()), f"{time.time()-t0:.0f}s")

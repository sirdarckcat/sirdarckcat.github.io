# Turn a pool of residue vectors (pool_Q*_m*_seed*.json from tempering.py, several files allowed)
# into a list of specs in the schema of goldbach/phd/campaign3/specs_variants.json.
#   python3 mkspecs.py OUT NAMEPREFIX COUNT CEILING_DIGITS pool1.json [pool2.json ...]
# Every vector is re-checked here with code that shares nothing with the sampler.
import json, math, sys
out, prefix, count, ceil_d = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
pools = [json.load(open(f)) for f in sys.argv[5:]]
Q = pools[0]["Q"]; mods = pools[0]["mods"]
assert all(p["Q"] == Q and p["mods"] == mods for p in pools)
def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
assert all(is_prime(r) and r > 2 for r in mods) and len(set(mods)) == len(mods)
rows = [q for q in range(3, Q) if is_prime(q)]
seen = {}
for p in pools:
    for k, v in p["pool"]:
        seen.setdefault(tuple(v), k)
vecs = sorted(seen.items(), key=lambda kv: (kv[1], kv[0]))[:count]
boost = 2.0; M = 2
for r in mods: boost *= r / (r - 1); M *= r
LN = 199 * math.log(10)
specs = []
for i, (v, kclaim) in enumerate(vecs):
    cover = list(zip(mods, v))
    assert all(0 < a < r for r, a in cover)
    residual = [q for q in rows if all(q % r != a for r, a in cover)]
    assert len(residual) == kclaim, (len(residual), kclaim)
    N0 = 0; mod = 2
    for r, a in cover:
        N0 = N0 + mod * (((a - N0) * pow(mod, -1, r)) % r); mod *= r
    assert mod == M and N0 % 2 == 0 and all(N0 % r == a for r, a in cover) and 0 <= N0 < M
    specs.append({"Q": Q, "cover": [[r, a] for r, a in cover], "residual": residual, "boost": boost,
                  "m_digits": math.log10(M), "E": len(residual) * boost / LN, "n_digits_est": 199.0,
                  "N0": str(N0), "M": str(M), "name": "%s_v%d" % (prefix, i),
                  # the GPU kernel holds k in 32 bits: kmax is capped below 2^32
                  "kmax": min((10 ** ceil_d - N0) // M, 2 ** 32 - 1), "ceiling_digits": ceil_d,
                  "stop_on_success": True})
assert len({s["N0"] for s in specs}) == len(specs)
json.dump(specs, open(out, "w"))
hist = {}
for s in specs: hist[len(s["residual"])] = hist.get(len(s["residual"]), 0) + 1
print("%s: %d specs, Q %d, %d moduli, M %.2f digits, rows left -> number of specs: %s, E(199 digits) %.3f to %.3f" % (
    out, len(specs), Q, len(mods), math.log10(M), dict(sorted(hist.items())), specs[0]["E"], specs[-1]["E"]))

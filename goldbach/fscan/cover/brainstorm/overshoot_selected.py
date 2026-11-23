# Overshoot of successes found with selection (emptiest 3% after a sieve to 1e6): rows survived beyond Q.
import json, math, sys
spec = json.load(open(sys.argv[1]))[0]; found = [json.loads(l) for f in sys.argv[2:] for l in open(f)]
Q = spec["Q"]; cover = [tuple(c) for c in spec["cover"]]; boost = spec["boost"]
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
G = max(f["g"] for f in found)
unc = [q for q in primes_upto(G + 1) if q >= Q and all(q % r != a for r, a in cover)]
import bisect
xs = [bisect.bisect_left(unc, f["g"]) for f in found]          # uncovered primes in [Q, g)
assert all(f["g"] in unc for f in found)                        # g itself is an uncovered prime
p = boost / math.log(int(found[0]["N"])); mean = (1 - p) / p; n = len(xs)
m = sum(xs) / n; sd = math.sqrt(1 - p) / p
print(f"Q = {Q}: {n} successes with selection; rows survived beyond Q: mean {m:.1f}, model {mean:.1f}, ratio {m/mean:.3f} +- {sd/mean/math.sqrt(n):.3f}; mean g - Q = {sum(f['g'] for f in found)/n - Q:.0f}")
# tail check: fraction surviving at least u rows against (1 - p)^u
for u in (20, 40, 80, 120, 160, 200):
    print(f"   survived >= {u:3d} rows: {sum(x >= u for x in xs)/n:.4f}   model {(1-p)**u:.4f}")

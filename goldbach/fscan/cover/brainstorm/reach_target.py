# Chance that a campaign reaches a target g, by design threshold, with near-misses counted.
#   python3 brainstorm/reach_target.py [target=213070] [days=9] [rate=29e6] [record_in_hand=157837] [extra cover files ...]
#   (run from cover/)
# A member has g >= x with probability RATIO * (1 - p)^U(x), U(x) = primes below x left uncovered by its cover, so the
# number of members with g >= target is Poisson with mean  n * RATIO * (1 - p)^U(target),  n = rate * 86400 * days.
# Only U(target) matters for the target; the expected final record depends on the whole profile.
import bisect, math, os, sys
target = int(sys.argv[1]) if len(sys.argv) > 1 else 213070
days = float(sys.argv[2]) if len(sys.argv) > 2 else 9.0
rate = float(sys.argv[3]) if len(sys.argv) > 3 else 29e6
hand = int(sys.argv[4]) if len(sys.argv) > 4 else 157837
extra = sys.argv[5:]
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89; TOP = 320000
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
P = [q for q in primes_upto(TOP) if q > 2]
def best_cover(path):
    best = None
    for line in open(path):
        t = line.split()
        if t and t[0] in ("COVER", "BEST"):
            k = float(t[1]) if t[0] == "COVER" else 0
            if best is None or k < best[0]: best = (k, [tuple(map(int, x.split(":"))) for x in t[(2 if t[0] == "COVER" else 1):]])
    return best[1]
here = os.path.dirname(os.path.abspath(__file__))
files = []
for Q in (150000, 160000, 170000, 180000, 190000, 200000, 213070):
    for f in (f"starts/q{Q}.txt", f"{here}/price/run_{Q}.txt"):
        if os.path.exists(f): files.append((str(Q), f)); break
files += [(os.path.basename(f), f) for f in extra]
n = rate * 86400 * days
print(f"target {target} ({target/21307.04:.2f}% of the ceiling); {days:g} fleet-days at {rate/1e6:.0f}M effective full-weight members/s; record in hand {hand}")
print("cover designed for | uncovered rows below the target | expected members reaching it | chance | fleet-days for one expected | expected final record")
for name, f in files:
    cov = best_cover(f); U = [q for q in P if all(q % r != a for r, a in cov)]
    u = bisect.bisect_left(U, target); mean = n * RATIO * (1 - p) ** u
    tot, x = 0.0, hand
    while x < TOP - 50:
        x += 50; b = math.exp(-n * RATIO * (1 - p) ** bisect.bisect_left(U, x)); tot += (1 - b) * 50
        if b > 1 - 1e-10: break
    print(f"{name} | {u} | {mean:.2e} | {100*(1-math.exp(-mean)):.4f}% | {days/mean:,.0f} | {hand+tot:.0f}")

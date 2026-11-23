# What a fixed budget of fleet time is worth at each design threshold.
#   python3 brainstorm/portfolio_budget.py [days=9.3] [rate=29e6] [record_in_hand=146191]       (run from cover/)
# rate: effective full-weight members per second of the whole fleet (29e6 on 23 Nov 02:08Z, deep sieve included).
# A member has g >= x with probability RATIO * (1 - p)^U(x), U(x) = the primes below x that its cover leaves
# uncovered (RATIO = 0.89 measured by the fleet at the design threshold).  Members are independent, so
# P(no member with g >= x) = exp(-n RATIO (1 - p)^U(x)).  Two ways of reporting:
#   "successes only": a member is reported when all rows below the design Q are composite (the search as it is);
#   "every first prime row": the row at which a tested member dies is logged when it beats the record in hand
#       (the kernel already finds that row: it stops each member at its first probable prime, rows ascending).
# Covers: the best in starts/q<Q>.txt, and the BEST line of brainstorm/price/run_<Q>.txt for 180,000 and above.
import bisect, math, os, sys
days = float(sys.argv[1]) if len(sys.argv) > 1 else 9.3
rate = float(sys.argv[2]) if len(sys.argv) > 2 else 29e6
hand = int(sys.argv[3]) if len(sys.argv) > 3 else 146191
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89; TOP = 300000
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
            k = int(t[1]) if t[0] == "COVER" else 0
            if best is None or k < best[0]: best = (k, [tuple(map(int, x.split(":"))) for x in t[(2 if t[0] == "COVER" else 1):]])
    return best[1]
here = os.path.dirname(os.path.abspath(__file__))
paths = {Q: f"starts/q{Q}.txt" for Q in (150000, 155000, 160000, 165000, 170000)}
paths.update({Q: f"{here}/price/run_{Q}.txt" for Q in (180000, 190000)})
U = {}
for Q, f in paths.items():
    cover = best_cover(f)
    U[Q] = [q for q in P if all(q % r != a for r, a in cover)]
n = rate * 86400 * days
def expected_record(Q, late):
    tot, x, step = 0.0, hand, 50
    while x < TOP - step:
        x += step
        u = bisect.bisect_left(U[Q], x if (late or x > Q) else Q)
        pr = 1 - math.exp(-n * RATIO * (1 - p) ** u)
        tot += pr * step
        if pr < 1e-9 and x > Q: break
    return hand + tot
print(f"{days} fleet-days at {rate/1e6:.1f}M effective full-weight members/s; record in hand {hand}; ceiling 2,130,704")
print("design Q | rows below Q | expected successes | expected record: successes only | every first prime row logged | P(no success)")
for Q in sorted(U):
    k = bisect.bisect_left(U[Q], Q); ns = n * RATIO * (1 - p) ** k
    a, b = expected_record(Q, False), expected_record(Q, True)
    print(f"{Q} | {k} | {ns:6.1f} | {a:7.0f} ({a/21307.04:.2f}%) | {b:7.0f} ({b/21307.04:.2f}%) | {math.exp(-ns):.3f}")

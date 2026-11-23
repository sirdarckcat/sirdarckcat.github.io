# What a fixed budget of fleet time is worth at each design threshold.
#   python3 brainstorm/portfolio_budget.py [days=9.3] [rate=29e6] [record_in_hand=146191] [hours at 150,000 first=0]
#   (run from cover/)
# rate: effective full-weight members per second of the whole fleet (29e6 on 23 Nov 02:08Z, deep sieve included).
# A member has g >= x with probability RATIO * (1 - p)^U(x), U(x) = the primes below x that its cover leaves
# uncovered (RATIO = 0.89: the fleet's logged expectation against (1 - p)^k).  Members are independent, so
# P(no member with g >= x) = exp(-n RATIO (1 - p)^U(x)), and phases multiply.  Two ways of reporting:
#   "successes only": a member is reported when all rows below the design Q are composite;
#   "near-misses counted": the row at which a tested member dies is reported when it beats the record in hand
#       (the kernel stops each member at its first probable prime, rows ascending; in the fleet's search since
#       23 Nov 02:40Z).
# Covers: the best in starts/q<Q>.txt; brainstorm/price/run_<Q>.txt (BEST line) where there is no starts file.
import bisect, math, os, sys
days = float(sys.argv[1]) if len(sys.argv) > 1 else 9.3
rate = float(sys.argv[2]) if len(sys.argv) > 2 else 29e6
hand = int(sys.argv[3]) if len(sys.argv) > 3 else 146191
first150 = float(sys.argv[4]) / 24 if len(sys.argv) > 4 else 0.0
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89; TOP = 300000; STEP = 20
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
U = {}
for Q in (150000, 155000, 160000, 165000, 167500, 170000, 172500, 175000, 177500, 180000, 190000):
    f = f"starts/q{Q}.txt" if os.path.exists(f"starts/q{Q}.txt") else f"{here}/price/run_{Q}.txt"
    if not os.path.exists(f): continue
    cover = best_cover(f)
    U[Q] = [q for q in P if all(q % r != a for r, a in cover)]
def log_none(Q, d, x, late):                  # ln P(no reported member with g >= x in d days at design Q)
    u = bisect.bisect_left(U[Q], x if (late or x > Q) else Q)
    return -rate * 86400 * d * RATIO * (1 - p) ** u
def outcome(phases, late):                    # expected final record, P(no improvement), 10% / 50% / 90% points
    tot, x, qs = 0.0, hand, {}
    none = math.exp(sum(log_none(Q, d, hand + 1, late) for Q, d in phases))
    while x < TOP - STEP:
        x += STEP
        below = math.exp(sum(log_none(Q, d, x, late) for Q, d in phases))      # P(final record < x)
        tot += (1 - below) * STEP
        for u in (0.1, 0.5, 0.9):
            if u not in qs and below >= u: qs[u] = x
        if below > 1 - 1e-9: break
    return hand + tot, none, qs
print(f"{days} fleet-days at {rate/1e6:.1f}M effective full-weight members/s; record in hand {hand}; ceiling 2,130,704"
      + (f"; the first {first150*24:g} h at 150,000" if first150 else ""))
print("design Q | rows below Q | expected record, successes only | near-misses counted (% of ceiling) | 10% / median / 90% | P(no improvement), near-misses counted")
for Q in sorted(U):
    ph = ([(150000, first150)] if first150 else []) + [(Q, days - first150)]
    a = outcome(ph, False)[0]; b, none, qs = outcome(ph, True)
    print(f"{Q} | {bisect.bisect_left(U[Q], Q)} | {a:7.0f} | {b:7.0f} ({b/21307.04:.2f}%) | {qs.get(0.1)} / {qs.get(0.5)} / {qs.get(0.9)} | {none:.4f}")

# Row weights for ptcover_w: weight(q) = 64 * P(the campaign's final record ends above q), from the model of
# portfolio_budget.py for a reference design.  A row far below the expected record weighs 64 (it must be composite in
# every member that can become the record); a row far above it weighs 0.
#   python3 brainstorm/soft_weights.py [days=10] [rate=29e6] [record_in_hand=157837] [design=170000] > weights.txt
import bisect, math, sys
days = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
rate = float(sys.argv[2]) if len(sys.argv) > 2 else 29e6
hand = int(sys.argv[3]) if len(sys.argv) > 3 else 157837
design = int(sys.argv[4]) if len(sys.argv) > 4 else 170000
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89; TOP = 200000
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
P = [q for q in primes_upto(TOP) if q > 2]
best = None
for line in open(f"starts/q{design}.txt"):
    t = line.split()
    if best is None or int(t[1]) < best[0]: best = (int(t[1]), [tuple(map(int, x.split(":"))) for x in t[2:]])
U = [q for q in P if all(q % r != a for r, a in best[1])]
n = rate * 86400 * days
for q in P:
    w = 1.0 if q < hand else 1 - math.exp(-n * RATIO * (1 - p) ** bisect.bisect_right(U, q))   # P(some member has g > q)
    wi = round(64 * w)
    if wi > 0: print(q, wi)

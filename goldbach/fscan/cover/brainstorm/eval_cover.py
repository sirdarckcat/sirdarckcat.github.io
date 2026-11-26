# Expected final record of a campaign run entirely on one cover (near-misses counted), and its weighted row count.
#   python3 brainstorm/eval_cover.py weights.txt days rate record_in_hand file [file ...]     (run from cover/)
# Each file: cover lines ("COVER k r:a ..." or "BEST r:a ..."); the first `BEST` line or the lowest-k COVER line is used.
import bisect, math, sys
wfile, days, rate, hand = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89; TOP = 300000; STEP = 20
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
P = [q for q in primes_upto(TOP) if q > 2]
W = dict(tuple(map(int, l.split())) for l in open(wfile))
def covers(path):
    best = None
    for line in open(path):
        t = line.split()
        if t and t[0] == "BEST": return [tuple(map(int, x.split(":"))) for x in t[1:]]
        if t and t[0] == "COVER":
            k = float(t[1])
            if best is None or k < best[0]: best = (k, [tuple(map(int, x.split(":"))) for x in t[2:]])
    return best[1]
n = rate * 86400 * days
print("file | rows below 160k / 165k / 170k / 172.5k / 175k / 180k | weighted rows | expected final record | P(no improvement)")
for f in sys.argv[5:]:
    cov = covers(f); U = [q for q in P if all(q % r != a for r, a in cov)]
    wr = sum(W.get(q, 0) for q in U) / 64
    tot, x = 0.0, hand
    while x < TOP - STEP:
        x += STEP
        below = math.exp(-n * RATIO * (1 - p) ** bisect.bisect_left(U, x)); tot += (1 - below) * STEP
        if below > 1 - 1e-9: break
    none = math.exp(-n * RATIO * (1 - p) ** bisect.bisect_left(U, hand + 1))
    print(f"{f.split('/')[-1]} | {' / '.join(str(bisect.bisect_left(U, x)) for x in (160000, 165000, 170000, 172500, 175000, 180000))} | {wr:.1f} | {hand + tot:.0f} ({(hand + tot)/21307.04:.2f}%) | {none:.4f}")

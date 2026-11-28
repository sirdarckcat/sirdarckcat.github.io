# Rank covers by what the campaign is after: the expected final record with near-misses counted.
#
#   python3 brainstorm/rank_covers.py days rate record_in_hand Q out.txt file [file ...] [--within X]     (run from cover/)
#
# Every cover line ("COVER k r:a ...") of the files is scored with the model of portfolio_budget.py, for a campaign
# of `days` at `rate` effective members a second run entirely on that cover: a member has g >= x with probability
# RATIO * (1 - p)^U(x), U(x) = the primes below x the cover leaves uncovered (all x, also above the design Q), p
# from the cover's own moduli.  Printed per file: rows below Q, rows below the record in hand, and the expected final
# record, for the best cover by plain row count and for the best by expected record; and how the two aims trade
# within the file.  out.txt receives all covers, best expected record first, as
# "COVER k r:a ..." lines (k = rows below Q), ready to be a starts/ file; with --within X only the covers whose
# expected record is within X of the best one (the walks of covergen start from any cover of a starts/ file, so
# a file of the best family gives a supply of that family).
#
# As a module: m = Model(days, rate, record_in_hand, Q); m.score(cover) -> (rows below Q, rows below the record,
# expected final record); m.weights() -> what one more uncovered row at q costs, as a fraction of a row below the
# record (the row weights of the planning model, for a reference profile of uncovered rows).
import math, sys
import numpy as np

RATIO = 0.89; TOP = 260000; STEP = 20; lnN = 200 * math.log(10)

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

def read_covers(path):
    for line in open(path):
        t = line.split()
        if t and t[0] == "COVER": yield [tuple(map(int, x.split(":"))) for x in t[2:]]

class Model:
    def __init__(self, days, rate, hand, Q):
        self.hand, self.Q = hand, Q
        self.P = np.array([q for q in primes_upto(TOP) if q > 2])
        self.xs = np.arange(hand + STEP, TOP, STEP); self.n = rate * 86400 * days
        self.iQ, self.iG = int(np.searchsorted(self.P, Q)), int(np.searchsorted(self.P, hand))
        self.ix = np.searchsorted(self.P, self.xs)                    # primes below each x
        self.rmod = {}

    def uncovered(self, cover):
        cov = np.zeros(len(self.P), dtype=bool)
        for r, a in cover:
            if r not in self.rmod: self.rmod[r] = (self.P % r).astype(np.int32)
            cov |= self.rmod[r] == a
        return ~cov

    def members_above(self, cover):
        """expected number of members with g >= x, for every x of self.xs"""
        cum = np.concatenate(([0], np.cumsum(self.uncovered(cover))))  # uncovered primes among the first i
        p = 2 * math.prod(r / (r - 1) for r, _ in cover) / lnN
        return cum, self.n * RATIO * (1 - p) ** cum[self.ix]

    def score(self, cover):
        cum, m = self.members_above(cover)
        return int(cum[self.iQ]), int(cum[self.iG]), self.hand + float(np.sum(1 - np.exp(-m))) * STEP

    def weights(self, cover):
        """cost of one more uncovered row at each prime of self.P, relative to a row below the record in hand:
        w(q) = int_{x > q} m e^-m dx / int_{x > record} m e^-m dx, m(x) = expected members with g >= x on `cover`"""
        _, m = self.members_above(cover)
        f = m * np.exp(-m)
        tail = np.concatenate((np.cumsum(f[::-1])[::-1], [0.0]))      # tail[j] = sum of f over xs[j:]
        j = np.searchsorted(self.xs, self.P, side="right")            # first x above q
        return tail[j] / tail[0]

if __name__ == "__main__":
    within = None
    if "--within" in sys.argv: i = sys.argv.index("--within"); within = float(sys.argv[i + 1]); del sys.argv[i:i + 2]
    days, rate, hand, Q, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    M = Model(days, rate, hand, Q)
    allc = []
    print(f"{days} days at {rate/1e6:.1f}M effective members/s, record in hand {hand}, design Q {Q}")
    print("file | covers | best by rows: rows below Q / below the record / expected record | best by expected record: the same three | "
          "among covers with the fewest rows: spread of rows below the record, and expected record per row moved below it")
    for f in sys.argv[6:]:
        rows = []
        for cover in read_covers(f):
            k, kg, e = M.score(cover); rows.append((k, kg, e, " ".join(f"{r}:{a}" for r, a in cover)))
        if not rows: continue
        allc += rows
        a = min(rows, key=lambda r: (r[0], -r[2])); b = max(rows, key=lambda r: r[2])
        kmin = min(r[0] for r in rows); lvl = [r for r in rows if r[0] <= kmin + 1]
        kg = np.array([r[1] for r in lvl], dtype=float); ee = np.array([r[2] for r in lvl])
        slope = np.polyfit(kg, ee, 1)[0] if len(lvl) > 5 and kg.std() > 0 else float("nan")
        print(f"{f.split('/')[-1]} | {len(rows)} | {a[0]} / {a[1]} / {a[2]:.0f} | {b[0]} / {b[1]} / {b[2]:.0f} | "
              f"{len(lvl)} covers within one row of {kmin}: rows below the record {kg.min():.0f} to {kg.max():.0f} (sd {kg.std():.1f}), "
              f"expected record {ee.min():.0f} to {ee.max():.0f}, {slope:+.0f} per row")
    allc.sort(key=lambda r: -r[2])
    if within is not None: allc = [r for r in allc if r[2] >= allc[0][2] - within]
    with open(out, "w") as g:
        seen = set()
        for k, kg, e, c in allc:
            if c not in seen: seen.add(c); g.write(f"COVER {k} {c}\n")
    print(f"{len(seen)} distinct covers written to {out}, best expected record first: {allc[0][2]:.0f} (rows {allc[0][0]}, below the record {allc[0][1]}) "
          f"down to {allc[-1][2]:.0f} (rows {allc[-1][0]}, below the record {allc[-1][1]})")

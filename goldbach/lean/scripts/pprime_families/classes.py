"""How the best members of the miniature sit in the residue classes of the primes beyond the line (29..199).
For a prime s the classes are ranked by the number of rows they strike (w_s(a) = #{rows q = a mod s}), best first."""
import math
import numpy as np
import pp

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(p) for p in np.nonzero(s)[0]]

ROWS = [p for p in primes_upto(999) if p > 2]
DEEP = [p for p in primes_upto(199) if p >= 29]
W = {s: np.bincount(np.array(ROWS) % s, minlength=s) for s in DEEP}
RANK = {}          # RANK[s][a] = position of class a when classes are sorted by weight, best first (ties by class)
for s in DEEP:
    order = np.lexsort((np.arange(s), -W[s])); r = np.empty(s, dtype=np.int64); r[order] = np.arange(s); RANK[s] = r

if __name__ == "__main__":
    N = np.asarray(pp.N); k2 = np.asarray(pp.K2); k1 = np.asarray(pp.K1); su = np.asarray(pp.SUCC)
    rng = np.random.default_rng(3)
    sets = {"all members (sample of 2,000,000)": rng.choice(len(N), 2000000, replace=False),
            "rows left at depth 200 <= 7 (13)": np.nonzero(k2 <= 7)[0], "<= 8 (62)": np.nonzero(k2 <= 8)[0],
            "<= 9 (401)": np.nonzero(k2 <= 9)[0], "<= 10 (1,965)": np.nonzero(k2 <= 10)[0], "<= 12 (33,598)": np.nonzero(k2 <= 12)[0],
            "the 256 successes": np.nonzero(su == 1)[0]}
    print("# classes of the primes 29..199 (37 primes), ranked by rows struck; share of each set of members that lies in the best class, the best 2, 3, the best third")
    print("set | mean rows left at depth 23 | mean number of primes (of 37) with N in: the best class | the best 2 | the best 3 | the best third | the same for the 8 primes 29..59: best class | best third")
    for name, idx in sets.items():
        n = N[idx].astype(np.int64)
        hit = {1: 0.0, 2: 0.0, 3: 0.0, "third": 0.0}; hit8 = {1: 0.0, "third": 0.0}
        for s in DEEP:
            r = RANK[s][n % s]
            for l in (1, 2, 3):
                hit[l] += float((r < l).mean())
            hit["third"] += float((r < s // 3).mean())
            if s <= 59:
                hit8[1] += float((r < 1).mean()); hit8["third"] += float((r < s // 3).mean())
        print(f"{name} | {k1[idx].mean():.1f} | {hit[1]:.2f} | {hit[2]:.2f} | {hit[3]:.2f} | {hit['third']:.2f} | {hit8[1]:.3f} | {hit8['third']:.2f}")
    # distribution of the number of best-class hits
    print("\n# number of primes 29..199 with N in the best class: distribution")
    print("set | 0 | 1 | 2 | 3 | 4 | 5 or more")
    for name, idx in sets.items():
        n = N[idx].astype(np.int64); h = np.zeros(len(n), dtype=np.int64)
        for s in DEEP: h += (RANK[s][n % s] < 1)
        c = np.bincount(np.minimum(h, 5), minlength=6) / len(n)
        print(f"{name} | " + " | ".join(f"{x:.4f}" for x in c))
    # incidences
    print("\n# incidences with the primes 29..199 (sum over the primes of the rows in the class of N), mean and standard deviation")
    for name, idx in sets.items():
        n = N[idx].astype(np.int64); inc = np.zeros(len(n), dtype=np.int64)
        for s in DEEP: inc += W[s][n % s]
        print(f"{name} | {inc.mean():.2f} | {inc.std():.2f}")

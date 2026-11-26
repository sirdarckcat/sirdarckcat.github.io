# A 200-digit campaign at a low threshold Q, where hits are frequent, to test two things with many hits:
#   (1) the number of hits against the model's (1 - p)^k per member,
#   (2) how far hits run past Q: the number x of cover-uncovered primes in [Q, g) should be geometric with parameter p.
# Also the hazard curve: P(the next tested row is a probable prime | m composite rows seen).
import sys, math, random, json, time
import numpy as np, gmpy2
from multiprocessing import Pool
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
from make_specs import crt_even, primes_upto
Q = int(sys.argv[1]); cover_file = sys.argv[2]; NMEM = int(float(sys.argv[3])); NPROC = int(sys.argv[4]); OUT = sys.argv[5]
SIEVE_B = 1 << 13; BEYOND = 90000
line = [l for l in open(cover_file) if l.startswith("BEST")][0].split()[1:]
cover = [tuple(map(int, x.split(":"))) for x in line]
mods = [r for r, _ in cover]
N0, M = crt_even(cover)
P = primes_upto(Q + BEYOND)
unc = lambda q: all(q % r != a for r, a in cover)
U = [q for q in P if 2 < q < Q and unc(q)]                    # uncovered rows below Q
UB = [q for q in P if Q <= q < Q + BEYOND and unc(q)]         # uncovered primes beyond Q
boost = 2.0
for r in mods: boost *= r / (r - 1)
SP = [s for s in primes_upto(SIEVE_B) if s > 2 and s not in set(mods)]
N0s = np.array([N0 % s for s in SP], dtype=np.int64); Ms = np.array([M % s for s in SP], dtype=np.int64); SPa = np.array(SP, dtype=np.int64)
tabU = [dict() for _ in SP]; tabB = [dict() for _ in SP]
for i, s in enumerate(SP):
    for j, q in enumerate(U): tabU[i].setdefault(q % s, []).append(j)
    for j, q in enumerate(UB): tabB[i].setdefault(q % s, []).append(j)
def work(seed):
    rng = random.Random(seed); out = {"members": 0, "hits": [], "first": {}, "exp": 0.0, "tests": 0, "prps": 0}
    t = rng.randrange(10**9, 5 * 10**9)
    for _ in range(NMEM // NPROC):
        t += 1; N = N0 + t * M
        res = (N0s + (t % SPa) * Ms) % SPa
        alive = [True] * len(U)
        for i, r in enumerate(res.tolist()):
            for j in tabU[i].get(r, ()): alive[j] = False
        rows = [j for j in range(len(U)) if alive[j]]
        rng.shuffle(rows)
        out["members"] += 1
        p = boost / math.log(N); out["exp"] += (1 - p) ** len(U)
        m = 0; dead = False
        for j in rows:
            n = N - U[j]; out["tests"] += 1
            if gmpy2.powmod(2, n - 1, n) == 1: dead = True; out["prps"] += 1; break
            m += 1
        if dead:
            out["first"][m] = out["first"].get(m, 0) + 1; continue
        # a hit: every prime below Q fails.  Now find g and count the uncovered primes survived beyond Q.
        aliveB = [True] * len(UB)
        for i, r in enumerate(res.tolist()):
            for j in tabB[i].get(r, ()): aliveB[j] = False
        x = 0; g = None
        for j, q in enumerate(UB):
            if aliveB[j]:
                n = N - q
                if gmpy2.powmod(2, n - 1, n) == 1: g = q; break
            x += 1
        out["hits"].append({"t": t, "g": g, "x": x, "rows_left": len(rows), "p": p})
    return out
if __name__ == "__main__":
    t0 = time.time()
    print(f"Q={Q}: {len(U)} uncovered rows below Q, {len(UB)} uncovered primes in [Q, Q+{BEYOND}), boost {boost:.3f}, sieve primes {len(SP)}", flush=True)
    with Pool(NPROC) as pool: res = pool.map(work, [1000 + i for i in range(NPROC)])
    mem = sum(r["members"] for r in res); hits = [h for r in res for h in r["hits"]]; exp = sum(r["exp"] for r in res)
    tests = sum(r["tests"] for r in res); prps = sum(r["prps"] for r in res)
    first = {}
    for r in res:
        for m, c in r["first"].items(): first[m] = first.get(m, 0) + c
    json.dump({"Q": Q, "members": mem, "expected": exp, "hits": hits, "first": first, "tests": tests, "prps": prps}, open(OUT, "w"))
    p = hits[0]["p"] if hits else boost / (200 * math.log(10))
    xs = [h["x"] for h in hits if h["g"] is not None]
    print(f"members {mem}, hits {len(hits)}, expected {exp:.1f}, ratio {len(hits)/exp if exp else float('nan'):.2f} +- {1/math.sqrt(max(1,len(hits))):.2f}; {time.time()-t0:.0f} s")
    if xs:
        mean_model = (1 - p) / p
        print(f"overshoot: uncovered primes survived beyond Q: mean {sum(xs)/len(xs):.1f}, model {mean_model:.1f}, ratio {sum(xs)/len(xs)/mean_model:.2f} +- {1/math.sqrt(len(xs)):.2f}; "
              f"mean g - Q = {sum(h['g'] - Q for h in hits if h['g'])/len(xs):.0f}; hits with no prime found within the window: {len(hits) - len(xs)}")
    # hazard by number of composite rows already seen
    tot = sum(first.values()) + len(hits); surv = tot
    print("hazard (probable prime at the next test | m composite rows seen), in blocks of 10:")
    for lo in range(0, 80, 10):
        at_risk = 0; events = 0; s = surv
        for m in range(lo, lo + 10):
            at_risk += s; e = first.get(m, 0); events += e; s -= e
        surv = s
        if at_risk: print(f"   m = {lo:2d}..{lo+9:2d}: {events}/{at_risk} = {events/at_risk:.4f}")

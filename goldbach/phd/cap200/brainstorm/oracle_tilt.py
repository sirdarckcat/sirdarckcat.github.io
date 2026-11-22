# The information optimum ("oracle floor") of the capped game on a large modulus set, by an
# explicit family: a cover on the first m moduli and an exponential tilt of the residues of N
# modulo every other prime r <= z,
#       P_theta(N mod r = c)  proportional to  exp(theta * j_r(c)),
# j_r(c) = number of uncovered rows q with q = c (mod r), i.e. the rows r kills for that class.
#   info(theta) = sum_r KL(P_theta || uniform)        nats: -ln(share of the progression kept)
#   rows(theta) = sum_q prod_r (1 - P_theta(class of q))  expected rows no prime <= z divides
#   E(theta)    = - sum_q ln(1 - s_q p_z),  s_q = prod_r (1 - P_theta(class of q)) the chance that no
#                 prime <= z divides the row, p_z = 2 prod_{3<=r<=z} r/(r-1) / ln N the chance that such
#                 a row is prime (at theta = 0 this is the cover's own E for every z, as it must be)
# The family has about exp(ln X - ln M_m - info) members below X, so it holds a success by the
# first moment when  ln M_m + info + E <= ln X.  This is an UPPER bound for the oracle floor.
# It is not constructive: nobody can list the members of the tilted family without enumerating
# the progression, which costs one nat of work per nat of info.
#   usage: python3 -I oracle_tilt.py POOL.json [ZMAX]
import json, math, sys, time
import numpy as np

d = json.load(open(sys.argv[1]))
ZMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
MLIST = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [88, 84, 80, 76, 72, 68, 64, 60, 56, 52, 48, 44, 40]
Q = d["Q"]; mods = [int(r) for r in d["mods"]]; k0, cls = d["pool"][0]
cls = [int(c) for c in cls]
LNX = 200 * math.log(10)

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

allp = [int(x) for x in primes_upto(max(Q, ZMAX)) if x >= 3]
P = np.array([q for q in allp if q < Q], dtype=np.int64)
thetas = np.round(np.concatenate([np.arange(0, 1.0, 0.02), np.arange(1.0, 2.01, 0.1)]), 3)
checkpoints = [z for z in (547, 1229, 10007, Q, 1000000, 10000000) if z <= ZMAX]
order = sorted(range(len(mods)), key=lambda i: mods[i])
print("Q = %d, %d rows, cover of %d moduli with %d rows left; ln X = %.2f" % (Q, len(P), len(mods), k0, LNX))
print("columns: z | m moduli kept (ln M) | rows left by the cover | best feasible theta | info | rows no prime <= z divides | p_z | E")
best_overall = {}
for m in MLIST:
    if m > len(mods): continue
    keep = [(mods[i], cls[i]) for i in order[:m]]
    kept = set(r for r, _ in keep)
    alive = np.ones(len(P), dtype=bool)
    for r, c in keep: alive &= (P % r != c)
    U = P[alive]; k = len(U)
    lnM = math.log(2) + sum(math.log(r) for r, _ in keep)
    logsurv = np.zeros((len(thetas), k)); info = np.zeros(len(thetas)); kills = np.zeros(len(thetas))
    lnboost = math.log(2); maxcls = (0, 0)
    ci = 0; t0 = time.time()
    for r in allp:
        if r > ZMAX: break
        while ci < len(checkpoints) and r > checkpoints[ci]:
            z = checkpoints[ci]; ci += 1
            pz = math.exp(lnboost) / LNX; rows = np.exp(logsurv).sum(axis=1); E = -np.log1p(-np.exp(logsurv) * pz).sum(axis=1)
            feas = lnM + info + E <= LNX
            if feas.any():
                j = int(np.argmin(np.where(feas, E, 1e9)))
                print("z=%7d | m=%2d (%.1f) | %5d | theta %.2f | info %6.1f | rows %7.1f | p %.4f | E %.2f   (theta=0: rows %.1f, E %.2f; spare nats at theta=0: %.1f)" % (
                    z, m, lnM, k, thetas[j], info[j], rows[j], pz, E[j], rows[0], E[0], LNX - lnM - E[0]))
                if z not in best_overall or E[j] < best_overall[z][0]: best_overall[z] = (E[j], m, thetas[j], info[j], rows[j])
            else:
                print("z=%7d | m=%2d (%.1f) | %5d | no feasible theta (E at theta=0: %.2f, needs %.1f nats more than there are)" % (z, m, lnM, k, E[0], lnM + E[0] - LNX))
        lnboost += math.log(r / (r - 1))
        if r in kept: continue
        res = U % r
        uniq, inv, cnt = np.unique(res, return_inverse=True, return_counts=True)
        if m == len(mods) and r > mods[order[-1]] and cnt.max() > maxcls[0]: maxcls = (int(cnt.max()), r)
        jmax = int(cnt.max())
        hist = np.bincount(cnt, minlength=jmax + 1).astype(np.float64); hist[0] = r - len(uniq)   # classes by row count
        js = np.arange(jmax + 1)
        w = np.exp(np.outer(thetas, js))                      # theta x j
        Z = (w * hist).sum(axis=1) / r
        mean = (w * hist * js).sum(axis=1) / (r * Z)
        info += thetas * mean - np.log(Z); kills += mean
        T = np.log1p(-w / (r * Z)[:, None])                   # log survival of a row whose class holds j rows
        logsurv += T[:, cnt[inv]]
    while ci < len(checkpoints):
        z = checkpoints[ci]; ci += 1
        pz = math.exp(lnboost) / LNX; rows = np.exp(logsurv).sum(axis=1); E = -np.log1p(-np.exp(logsurv) * pz).sum(axis=1)
        feas = lnM + info + E <= LNX
        if feas.any():
            j = int(np.argmin(np.where(feas, E, 1e9)))
            print("z=%7d | m=%2d (%.1f) | %5d | theta %.2f | info %6.1f | rows %7.1f | p %.4f | E %.2f   (theta=0: rows %.1f, E %.2f; spare nats at theta=0: %.1f)" % (
                z, m, lnM, k, thetas[j], info[j], rows[j], pz, E[j], rows[0], E[0], LNX - lnM - E[0]))
            if z not in best_overall or E[j] < best_overall[z][0]: best_overall[z] = (E[j], m, thetas[j], info[j], rows[j])
        else:
            print("z=%7d | m=%2d (%.1f) | %5d | no feasible theta" % (z, m, lnM, k))
    if m == len(mods):
        print("  largest class of uncovered rows modulo a prime above the cover and below %d: %d rows, at the prime %d" % (ZMAX, maxcls[0], maxcls[1]))
    print("  (m=%d done in %.0f s)" % (m, time.time() - t0)); sys.stdout.flush()
print("\nbest explicit family per z (an upper bound for the information optimum):")
for z in sorted(best_overall):
    E, m, th, inf, rows = best_overall[z]
    print("  primes up to %7d: E <= %.2f  (cover on %d moduli, theta %.2f, info %.1f nats, %.1f rows)" % (z, E, m, th, inf, rows))

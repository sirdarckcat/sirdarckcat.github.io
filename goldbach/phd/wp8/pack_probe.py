"""Cover-packing headroom probe.

Question: greedy class-per-modulus covers leave ~7.6% of primes < Q
uncovered (Mertens-like overlap loss). Does JOINT optimization of the
class assignment (coordinate ascent + random kicks) recover coverage at
the same modulus budget?  Every extra prime covered saves boost/lnN
nats of E — the campaign exponent — at zero additional cost.

Baselines: c1 cover (Q=122,000, 88 moduli, |U|=867) and a from-scratch
greedy at Q=200,000 with the same moduli set.
"""
import json, math, sys, time
import numpy as np
from sympy import primerange

t0 = time.time()
spec = json.load(open('goldbach/phd/campaign3/base_spec.json'))
moduli = [int(r) for r, a in spec['cover']]
classes_c1 = {int(r): int(a) for r, a in spec['cover']}
boost = float(spec['boost'])
LNN = 199 * math.log(10)


def build(Q):
    P = np.array(list(primerange(3, Q)), dtype=np.int64)
    res = {r: (P % r).astype(np.int32) for r in moduli}
    return P, res


def uncovered_count(P, res, assign):
    cc = np.zeros(len(P), dtype=np.int16)
    for r, a in assign.items():
        cc += (res[r] == a)
    return cc, int((cc == 0).sum())


def ascent(P, res, assign, rng, sweeps_max=60):
    cc, u = uncovered_count(P, res, assign)
    order = list(assign)
    improved = True
    s = 0
    while improved and s < sweeps_max:
        improved = False
        s += 1
        rng.shuffle(order)
        for r in order:
            a_old = assign[r]
            m_old = res[r] == a_old
            cc -= m_old
            free = cc == 0
            hist = np.bincount(res[r][free], minlength=r)
            a_new = int(hist.argmax())
            if a_new != a_old and hist[a_new] > hist[a_old]:
                assign[r] = a_new
                improved = True
            cc += (res[r] == assign[r])
        u = int((cc == 0).sum())
    return assign, u


def kicks(P, res, assign, u_best, rng, rounds=40, kick=6):
    best = dict(assign)
    for _ in range(rounds):
        cand = dict(best)
        for r in rng.choice(moduli, size=kick, replace=False):
            cand[int(r)] = int(rng.integers(1, int(r)))
        cand, u = ascent(P, res, cand, rng)
        if u < u_best:
            u_best, best = u, dict(cand)
    return best, u_best


def greedy(P, res):
    cc = np.zeros(len(P), dtype=np.int16)
    assign = {}
    for r in moduli:                      # ascending, like cover.py
        free = cc == 0
        hist = np.bincount(res[r][free], minlength=r)
        a = int(hist.argmax())
        assign[r] = a
        cc += (res[r] == a)
    return assign, int((cc == 0).sum())


def report(tag, Q, nP, u):
    E = u * boost / LNN
    print(f"{tag}: Q={Q} primes={nP} |U|={u} cov={100*(1-u/nP):.2f}% "
          f"E={E:.2f}", flush=True)


rng = np.random.default_rng(7)

# --- Q = 122,000 (c1's own game) ---
Q = 122000
P, res = build(Q)
cc, u0 = uncovered_count(P, res, dict(classes_c1))
report("c1 baseline (greedy)", Q, len(P), u0)
a1, u1 = ascent(P, res, dict(classes_c1), rng)
report("after coordinate ascent", Q, len(P), u1)
a2, u2 = kicks(P, res, a1, u1, rng)
report("after kicks", Q, len(P), u2)

# --- Q = 200,000 (the ambition target) ---
Q = 200000
P, res = build(Q)
g0, ug = greedy(P, res)
report("greedy from scratch", Q, len(P), ug)
a1, u1 = ascent(P, res, dict(g0), rng)
report("after coordinate ascent", Q, len(P), u1)
a2, u2 = kicks(P, res, a1, u1, rng)
report("after kicks", Q, len(P), u2)
json.dump(sorted((int(r), int(a)) for r, a in a2.items()),
          open(sys.argv[1] if len(sys.argv) > 1 else
               '/tmp/claude-0/-home-user-sirdarckcat-github-io/70feb86a-ee78-5557-8d35-c04b913db398/scratchpad/pack200k_best.json', 'w'))
print(f"done in {time.time()-t0:.0f}s", flush=True)

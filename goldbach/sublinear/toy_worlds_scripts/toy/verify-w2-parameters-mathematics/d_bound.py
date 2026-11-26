# Verifier's Theorem V (random-list model): E|G| = q^n P(A >= D0) < q^(1 + mu_W + sigma),
#   mu_W = sum over weighted classes (i,c) of d_i / q^(2 d_i),  sigma = (n-1) - (sqrt(n-1) - (n-1)/(2||s||))_+^2.
import math, random, itertools
def Mn(n, D):
    if D <= 0: return 0
    J = (D - 1) // (n - 1); return (J + 1) * D - (n - 1) * J * (J + 1) // 2
rng = random.Random(7)
worst = -1e9; cnt = 0; nontriv = 0; examples = []
for trial in range(40000):
    q = rng.choice([2, 3, 4, 5, 7, 8, 13])
    n = rng.randint(2, 7)
    npl = rng.randint(1, 10)
    places = []
    for _ in range(npl):
        d = rng.choice([1, 1, 1, 2, 2, 3])
        Q = q ** d
        kind = rng.choice(["pin", "sparse", "dense", "full", "soft"])
        if kind == "pin": prof = {rng.randint(1, 12): 1}
        elif kind == "sparse": prof = {rng.randint(1, 8): rng.randint(1, max(1, min(3, Q - 1)))}
        elif kind == "dense": prof = {rng.randint(1, 6): rng.randint(max(1, Q // 2), Q - 1) if Q > 2 else 1}
        elif kind == "full": prof = {rng.randint(1, 4): Q}
        else:
            prof = {}
            left = Q
            for sv in rng.sample(range(1, 10), 3):
                c = rng.randint(0, left); prof[sv] = c; left -= c
            prof = {k: v for k, v in prof.items() if v > 0} or {1: 1}
        places.append((d, Q, prof))
    C = sum(d * c * s * (s + 1) // 2 for d, Q, prof in places for s, c in prof.items())
    s2 = sum(d * c * s * s for d, Q, prof in places for s, c in prof.items())
    D0 = 1
    while Mn(n, D0) <= C: D0 += 1
    # exact distribution of A
    dist = {0: 1.0}
    for d, Q, prof in places:
        nw = sum(prof.values())
        new = {}
        for a, pr in dist.items():
            if Q - nw: new[a] = new.get(a, 0) + pr * (Q - nw) / Q
            for s, c in prof.items():
                new[a + d * s] = new.get(a + d * s, 0) + pr * c / Q
        dist = new
    P = sum(pr for a, pr in dist.items() if a >= D0)
    if P <= 0: cnt += 1; continue
    EG = q ** n * P
    muW = sum(d * sum(prof.values()) / Q ** 2 for d, Q, prof in places)
    sig = (n - 1) - max(0.0, math.sqrt(n - 1) - (n - 1) / (2 * math.sqrt(s2))) ** 2
    bound = q ** (1 + muW + sig)
    cnt += 1; nontriv += 1
    r = math.log(EG / bound)
    if r > worst: worst = r; examples.append((round(r, 3), q, n, [(d, prof) for d, Q, prof in places], D0, round(EG, 3), round(bound, 3)))
print("instances:", cnt, "with P(A>=D0)>0:", nontriv, "max ln(E|G| / bound):", worst)
for e in examples[-4:]: print("  ", e)

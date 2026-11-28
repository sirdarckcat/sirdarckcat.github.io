# World 4, Theorem W4.3 checked by brute force: the width of the minimal read-once DP over the places (in a fixed order) that
# recognises the integer window W = {N < K}, viewed in prod Z/s_i, is the number of distinct residual sets
# {x_B : (x_A, x_B) in W} over prefixes x_A at each cut A | B. Claimed: between min(P_A, P_B, K) and 2 min(P_A, P_B, K).
#   python3 width_toy.py > width_toy.out
import math, itertools
def width_profile(places, K):
    out = []
    for j in range(len(places) + 1):
        A, B = places[:j], places[j:]
        res = {}
        for N in range(K):
            pa = tuple(N % s for s in A); pb = tuple(N % s for s in B)
            res.setdefault(pa, set()).add(pb)
        distinct = len({frozenset(v) for v in res.values()})
        PA = math.prod(A); PB = math.prod(B)
        out.append((j, PA, PB, distinct, min(PA, PB, K)))
    return out
for places, K in (([5, 7, 11, 13, 17, 19, 23], 2000), ([23, 19, 17, 13, 11, 7, 5], 2000), ([7, 23, 5, 19, 11, 17, 13], 5000),
                  ([29, 31, 37, 41, 43], 3000)):
    print(f"places {places}, K = {K}, P = {math.prod(places):,} (P >= K^2: {math.prod(places) >= K * K})")
    ok = True
    for j, PA, PB, d, m in width_profile(places, K):
        flag = m <= d <= 2 * m
        ok &= flag
        print(f"   cut {j}: P_A = {PA:>9,}  P_B = {PB:>9,}  distinct residual sets {d:>6,}  min(P_A,P_B,K) {m:>6,}  {'ok' if flag else 'OUTSIDE'}")
    mx = max(d for _, _, _, d, _ in width_profile(places, K))
    print(f"   max width {mx:,} (K = {K:,}); claim min(P_A, P_B, K) <= width <= 2 min(...) at every cut: {ok}")

"""(c)1: the Fermat condition of k survivors of one member at once: 2^(N-1) mod P, P = prod (N - q_i), then the remainders
(a product / remainder tree) and the check 2^(N-1) = 2^q_i mod (N - q_i), against k separate powmods (GMP via gmpy2) at 665 bits."""
import time, gmpy2
lines = [l.split() for l in open("surv.txt").read().splitlines()]
k0 = lines[0][0]
mem = [(int(q), gmpy2.mpz(n)) for kk, q, prp, n in lines if kk == k0]
N = mem[0][1] + mem[0][0]
def single(ms):
    return [gmpy2.powmod(2, n - 1, n) == 1 for q, n in ms]
def tree(ms):
    # product tree
    lev = [[n for q, n in ms]]
    while len(lev[-1]) > 1:
        a = lev[-1]; lev.append([a[i] * a[i + 1] if i + 1 < len(a) else a[i] for i in range(0, len(a), 2)])
    x = gmpy2.powmod(2, N - 1, lev[-1][0])
    rem = [x]
    for l in reversed(lev[:-1]):
        rem = [rem[i // 2] % l[i] for i in range(len(l))]
    return [rem[i] == gmpy2.powmod(2, q, n) for i, (q, n) in enumerate(ms)]
def best(f, ms, reps):
    b = 1e9
    for _ in range(reps):
        t = time.perf_counter(); r = f(ms); b = min(b, time.perf_counter() - t)
    return b, r
t1, r1 = best(single, mem[:64], 5)
per = t1 / 64
print(f"one powmod at {N.bit_length()} bits (GMP): {per * 1e6:.1f} us")
for k in (2, 4, 8, 13, 16, 32, 64):
    tb, rb = best(tree, mem[:k], 5)
    assert rb == single(mem[:k])
    print(f"  k = {k:2d}: batch {tb * 1e6:8.1f} us = {tb / (k * per):5.2f} x the {k} separate powmods")

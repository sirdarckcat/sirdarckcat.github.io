#!/usr/bin/env python3
"""Exact-integer model of the proposed 3-limb AVX2 Fermat kernel (vpmuludq: 32x32->64).
Mirrors the C code operation for operation, and records the maximum of every intermediate (must stay < 2^64)."""
import random, sys, math

def inv_neg(n, W):                       # -n^-1 mod 2^W
    x = pow(n, -1, 1 << W)
    return (-x) % (1 << W)

class Stats:
    def __init__(s): s.mx = {}
    def see(s, name, v):
        assert 0 <= v < (1 << 64), (name, v.bit_length())
        if v > s.mx.get(name, 0): s.mx[name] = v

def step(a, nl, ni, W, bit, st):
    M = (1 << W) - 1
    a0, a1, a2 = a
    assert a0 <= M and a1 <= M and 2*a2 < (1 << 32) and 2*a1 < (1 << 32)   # vpmuludq reads low 32 bits only
    d1, d2 = 2*a1, 2*a2
    z = [a0*a0, a0*d1, a0*d2 + a1*a1, a1*d2, a2*a2]
    for i, v in enumerate(z): st.see(f"sq{i}", v)
    for i in range(3):
        m = (((z[i] & 0xFFFFFFFF) * ni) & 0xFFFFFFFFFFFFFFFF) & M
        for j in range(3):
            assert m < (1 << 32) and nl[j] < (1 << 32)
            z[i+j] += m * nl[j]
            st.see(f"red{i+j}", z[i+j])
        assert (z[i] & M) == 0, "low limb not cleared"
        z[i+1] += z[i] >> W
        st.see(f"carry{i+1}", z[i+1])
    z3, z4 = z[3] << bit, z[4] << bit
    st.see("z3sh", z3); st.see("z4sh", z4)
    z4 += z3 >> W
    st.see("z4c", z4)
    return [z3 & M, z4 & M, z4 >> W]

def fermat(n, W, st, t=None):
    """returns True iff 2^(n-1) = 1 mod n by the kernel's method"""
    Rb = 3 * W
    b = n.bit_length()
    if t is None: t = b - 6
    M = (1 << W) - 1
    ni = inv_neg(n, W)
    nl = [(n >> (W*j)) & M for j in range(3)]
    E = n + Rb - 1
    c = (E + (1 << t) - 1) >> t
    B = (c << t) - E
    assert 0 <= B < (1 << t) and 1 <= c <= Rb, (c, Rb)
    e = Rb - c
    y = 1 << e
    if y >= 4*n: y %= n
    a = [(y >> (W*j)) & M for j in range(3)]
    a[2] = y >> (2*W)
    assert y < 4*n
    for i in range(t):
        bit = (B >> (t - 1 - i)) & 1
        a = step(a, nl, ni, W, bit, st)
        val = a[0] + (a[1] << W) + (a[2] << (2*W))
        assert val < 4*n, ("value bound", i)          # input bound of the next step
    y = a[0] + (a[1] << W) + (a[2] << (2*W))
    if y >= 2*n: y -= 2*n
    if y >= n: y -= n
    return y == 1

def run(W, maxbits, trials, seed=1):
    random.seed(seed)
    st = Stats(); bad = 0; tot = 0; prp = 0
    cases = []
    for b in range(41, maxbits + 1):
        for _ in range(trials):
            n = random.getrandbits(b) | (1 << (b - 1)) | 1
            cases.append(n)
        # adversarial structure
        M = (1 << W) - 1
        cases += [(1 << b) - 1, (1 << (b-1)) + 1, (1 << b) - 3, (1 << (b-1)) | M | 1]
        cases += [((1 << b) - 1) & ~((1 << (b - W)) - 1) | M, ((1 << b) - 1) ^ (1 << (b // 2)) ]
    for n in cases:
        if n % 2 == 0 or n.bit_length() > maxbits or n.bit_length() < 41: continue
        want = pow(2, n - 1, n) == 1
        got = fermat(n, W, st)
        tot += 1; prp += want; bad += (want != got)
    return tot, prp, bad, st

if __name__ == "__main__":
    W = int(sys.argv[1]); maxbits = int(sys.argv[2]); trials = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    tot, prp, bad, st = run(W, maxbits, trials)
    print(f"W={W} Rb={3*W}  n up to {maxbits} bits: {tot} numbers, {prp} PRP, {bad} mismatches")
    worst = max(st.mx.items(), key=lambda kv: kv[1])
    print("  max column = 2^%.3f (%s)  [limit 2^64]" % (math.log2(worst[1]), worst[0]))
    print("  " + ", ".join(f"{k}:{math.log2(v):.2f}" for k, v in sorted(st.mx.items()) if v))
    sys.exit(bad != 0)

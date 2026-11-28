"""Limb-exact CPU model of gpu_fermat.py's kernel fermat2: the same 32-bit limbs (little-endian), the same
CIOS loop, the same conditional subtractions and the same exponent walk, with every u32/u64 wrap made
explicit. It is a reference for proofs and for checking the kernel's outputs, not for speed (~0.3 s a
test in CPython).

    python3 gpu_fermat_ref.py specs_variants.json [samples]     # the model against gmpy2

fermat2_ref(cq, M, k, L) returns 1 iff 2^(n-1) == 1 (mod n) for n = cq + k*M, exactly as the kernel
computes it (preconditions as in the kernel: n odd, n < 2^(32L), k < 2^32).
"""
import json, random, sys

MASK = 0xFFFFFFFF


def to_limbs(x, L):
    return [(x >> (32 * i)) & MASK for i in range(L)]


def from_limbs(a):
    return sum(v << (32 * i) for i, v in enumerate(a))


def mont_sqr(x, n, ninv, L):
    """x <- x*x*R^-1 mod n in place (CIOS with t[L+2]); x < n required."""
    t = [0] * (L + 2)
    for i in range(L):
        c, ai = 0, x[i]
        for j in range(L):                     # u64 s = t[j] + ai*x[j] + c  (never exceeds 2^64 - 1)
            s = t[j] + ai * x[j] + c
            t[j], c = s & MASK, s >> 32
        s = t[L] + c
        t[L], t[L + 1] = s & MASK, (s >> 32) & MASK
        m = (t[0] * ninv) & MASK               # u32 m = t[0] * ninv
        s = t[0] + m * n[0]
        c = s >> 32
        for j in range(1, L):
            s = t[j] + m * n[j] + c
            t[j - 1], c = s & MASK, s >> 32
        s = t[L] + c
        t[L - 1] = s & MASK
        t[L] = (t[L + 1] + (s >> 32)) & MASK   # u32 addition
    ge = t[L] != 0
    if not ge:
        ge = True                              # equal counts as >= (then x becomes 0)
        for j in range(L - 1, -1, -1):
            if t[j] != n[j]:
                ge = t[j] > n[j]
                break
    if ge:
        br = 0
        for j in range(L):                     # u64 d = t[j] - n[j] - br; x[j] = (u32)d; br = (d >> 63) & 1
            d = t[j] - n[j] - br
            x[j], br = d & MASK, 1 if d < 0 else 0
    else:
        for j in range(L):
            x[j] = t[j]


def dbl_mod(x, n, L):
    """x <- 2x mod n in place; x < n required."""
    carry = 0
    for j in range(L):
        v = x[j]
        x[j], carry = ((v << 1) | carry) & MASK, v >> 31
    ge = carry != 0
    if not ge:
        ge = True
        for j in range(L - 1, -1, -1):
            if x[j] != n[j]:
                ge = x[j] > n[j]
                break
    if ge:
        br = 0
        for j in range(L):
            d = x[j] - n[j] - br
            x[j], br = d & MASK, 1 if d < 0 else 0


def fermat2_ref(cq, M, k, L=21):
    """The kernel's computation for one thread: cq, M as integers, k < 2^32."""
    cql, Ml = to_limbs(cq, L), to_limbs(M, L)
    n, c = [0] * L, 0
    for j in range(L):                         # u64 s = Mv[j]*k + cq[j] + c
        s = Ml[j] * k + cql[j] + c
        n[j], c = s & MASK, s >> 32
    inv = n[0]
    for _ in range(5):                         # inv *= 2u - n[0]*inv  (u32)
        inv = (inv * ((2 - n[0] * inv) & MASK)) & MASK
    ninv = (-inv) & MASK
    x = [1] + [0] * (L - 1)
    for _ in range(32 * L):
        dbl_mod(x, n, L)                       # x = R mod n
    one = list(x)
    top = L - 1
    while top > 0 and n[top] == 0:
        top -= 1
    b = n[top].bit_length() - 1                # 31 - __clz(n[top])
    dbl_mod(x, n, L)                           # 2^1 for the top bit of n - 1
    for w in range(top, -1, -1):
        word = n[w] & (~1 & MASK) if w == 0 else n[w]
        for i in range((b - 1) if w == top else 31, -1, -1):
            mont_sqr(x, n, ninv, L)
            if (word >> i) & 1:
                dbl_mod(x, n, L)
    return int(x == one)


if __name__ == "__main__":
    specs = json.load(open(sys.argv[1]))
    S = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    rng = random.Random(1)
    bad = prps = 0
    for t in range(S):
        sp = specs[t % 2]
        U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
        N0, M = int(sp["N0"]), int(sp["M"])
        q = U[rng.randrange(len(U))]
        k = [0, 1, 2, 3, 247, 248, 4294967295][t] if t < 7 else rng.randrange(1 << 32)
        n = N0 - q + k * M
        ref = int(pow(2, n - 1, n) == 1)
        got = fermat2_ref(N0 - q, M, k)
        bad += got != ref
        prps += ref
    print(f"{S} candidates (k = 0, 1, 2, 3, 247, 248, 2^32 - 1, then random k < 2^32), {prps} base-2 PRPs, "
          f"mismatches against pow(2, n - 1, n): {bad}")

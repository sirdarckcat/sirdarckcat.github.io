# T5 step 2: from a cover (r:a pairs) to the members N_k = N0 + k*D, D = 2M, M = the product of the moduli, N0 = a_r (mod r) for
# every modulus and N0 even. Writes setup_<tag>.bin for sieve.c (rows left by the cover, N0 and D as 64-bit limbs) and
# setup_<tag>.json (N0, D, the rows, the moduli and classes).
#   python3 members.py cover_X4657.txt tag
import sys, json, math
import numpy as np
from cover import odd_primes_below, Q

def read_cover(path):
    return [tuple(map(int, w.split(":"))) for w in open(path).read().split("\n")[1].split()]

def crt(pairs):
    N, m = 0, 2                                                 # N = 0 (mod 2): N even
    for r, a in pairs:
        t = ((a - N) * pow(m, -1, r)) % r; N += m * t; m *= r
    return N % m, m

def limbs(n, nl): return np.array([(n >> (64 * i)) & ((1 << 64) - 1) for i in range(nl)], dtype=np.uint64)

if __name__ == "__main__":
    pairs = read_cover(sys.argv[1]); tag = sys.argv[2]
    N0, D = crt(pairs)
    assert all(N0 % r == a for r, a in pairs) and N0 % 2 == 0
    rows = odd_primes_below(Q).astype(np.int64)
    hit = np.zeros(len(rows), bool)
    for r, a in pairs: hit |= (rows % r == a)
    U = rows[~hit].astype(np.int32)
    nl = (D.bit_length() + 63) // 64
    with open(f"setup_{tag}.bin", "wb") as f:
        f.write(np.int32(len(U)).tobytes()); f.write(np.int32(nl).tobytes()); f.write(U.tobytes())
        f.write(limbs(N0, nl).tobytes()); f.write(limbs(D, nl).tobytes())
    json.dump(dict(Q=Q, moduli=[r for r, _ in pairs], classes=[a for _, a in pairs], X=max(r for r, _ in pairs), D=str(D), N0=str(N0),
                   rows_left=[int(q) for q in U], digits_D=len(str(D))), open(f"setup_{tag}.json", "w"))
    print(f"{len(pairs)} moduli up to {max(r for r, _ in pairs)}; D = 2M has {len(str(D))} digits; {len(U):,} rows left; {nl} limbs; "
          f"members N0 + k D below 10^d for k < 10^(d - {math.log10(D):.2f})")

"""The members of one cover, for the direct sieve: N = N0 + k M with M = 2 prod r, N0 even and in the class of every
modulus.  Writes for every prime s in (463, B] the residues N0 mod s and M mod s, and the rows of the cover.
  python members.py FILE Q LINE B OUTDIR"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of

path, Q, line, B, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(float(sys.argv[4])), sys.argv[5]
claimed, classes = read_covers(path)[line]
M = 2; N0 = 0
for r, a in sorted(classes.items()):               # Chinese remaindering, one modulus at a time; N0 stays even
    t = ((a - N0) * pow(M, -1, r)) % r
    N0 += t * M; M *= r
assert N0 % 2 == 0 and all(N0 % r == a for r, a in classes.items()) and 0 <= N0 < M
members = 10 ** 200 // M
rows = rows_of(classes, Q); assert len(rows) == claimed
# a row q is by definition a prime with N - q coprime to 2 and to every modulus
assert all(math.gcd(N0 - int(q), M) == 1 for q in rows)
PR = primes_upto(B); PR = PR[PR > 463]
r0 = np.array([N0 % int(s) for s in PR], dtype=np.uint32); m = np.array([M % int(s) for s in PR], dtype=np.uint32)
os.makedirs(out, exist_ok=True)
PR.astype(np.uint32).tofile(f"{out}/primes.u32"); r0.tofile(f"{out}/r0.u32"); m.tofile(f"{out}/m.u32"); rows.astype(np.uint32).tofile(f"{out}/rows.u32")
print(f"line {line}: {len(rows)} rows; M has {len(str(M))} digits; members below 10^200: {members:,d} = 2^{math.log2(members):.2f}; primes in (463, {B:.3g}]: {len(PR):,d}; N0 mod 10^9+7 = {N0 % (10**9 + 7)}")

"""Build a labelled sample of real rows: members N = N0 + kM of the 200,000 cover, every row sieved by all primes
below 10^8 (exactly as in the search), survivors labelled prime/composite by gmpy2.is_prime (BPSW + Miller-Rabin).
Output: survivors.pkl = list of (k, q, is_prime)."""
import sys, time, random, pickle, numpy as np, gmpy2
from gmpy2 import mpz
from common import setup
rows, cov, N0, M, K = setup()
NM = int(sys.argv[1]) if len(sys.argv) > 1 else 60
LIM = 10 ** 8
t0 = time.time()
sv = np.ones(LIM // 2, dtype=bool); sv[0] = False          # odd numbers 2i+1
for i in range(1, int(LIM ** .5) // 2 + 1):
    if sv[i]: sv[2 * i * (i + 1)::2 * i + 1] = False
P = (2 * np.nonzero(sv)[0] + 1).astype(np.uint64); del sv
covp = set(r for r, _ in cov)
P = P[P > 463]                                              # the cover primes are spent; 2 does not matter (N even, q odd)
small = P[P < 200000]; big = P[P >= 200000]
print(f"{len(P)} primes from 467 to 10^8, {time.time()-t0:.1f}s", flush=True)
isrow = np.zeros(200000, dtype=bool); isrow[rows] = True
random.seed(20261126)
out = []; tot = 0
for mi in range(NM):
    k = random.randrange(K); N = N0 + k * M
    # N mod p for all p, Horner on 32-bit limbs
    limbs = []; x = int(N)
    while x: limbs.append(x & 0xffffffff); x >>= 32
    r = np.zeros(len(P), dtype=np.uint64)
    for L in reversed(limbs):
        r = ((r << np.uint64(32)) + np.uint64(L)) % P
    assert int(r[12345]) == int(N % int(P[12345]))
    alive = isrow.copy()
    rs = r[:len(small)]
    for p, a in zip(small.tolist(), rs.tolist()):
        alive[a::p] = False                                 # q = a mod p  <=>  p | N - q   (N - q > p always)
    rb = r[len(small):]; rb = rb[rb < 200000]
    alive[rb.astype(np.int64)] = False
    surv = np.nonzero(alive)[0].tolist()
    for q in surv:
        out.append((k, q, bool(gmpy2.is_prime(N - q, 5))))
    tot += len(surv)
    if mi % 10 == 0: print(mi, len(surv), f"{time.time()-t0:.0f}s", flush=True)
pickle.dump(out, open("survivors.pkl", "wb"))
npr = sum(1 for _, _, b in out if b)
print(f"members {NM}, survivors {tot} ({tot/NM:.1f} per member, share of rows {tot/NM/len(rows):.4f}), primes {npr} ({npr/tot:.4f})")

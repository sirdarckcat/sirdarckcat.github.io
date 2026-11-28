# research's check 6 (a9e4a27; the lead's condition 1, 20:00Z): uncovered primes above Q in the consumed 463 vectors, chunks c186-c198 (first m89 starts, family A) against
# c200-c204 (58e95e3 starts: A + B). A prime q >= 170,000 is covered when q = N0 mod p for a cover prime p (then N - q has the factor p); otherwise it is a row a design hit
# still has to pass. Per chunk: mean count in [170,000, 175,000) and [175,000, 180,000), all 1,000 vectors.
import json, numpy as np
def primes(a, b):
    s = np.ones(b, bool); s[:2] = False
    for i in range(2, int(b ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s[a:])[0] + a
P1, P2 = primes(170000, 175000), primes(175000, 180000)
out = {}
import glob; CH = sorted(int(f[-11:-5]) for f in glob.glob("/content/vec491/vec_*.json"))[:6]
for c in CH:
    s = json.load(open(f"/content/vec491/vec_{c:06d}.json"))
    a1 = a2 = 0
    for v in s:
        cov = v["cover"] if isinstance(v["cover"], list) else json.loads(v["cover"])
        N0 = int(v["N0"])
        m1 = np.zeros(len(P1), bool); m2 = np.zeros(len(P2), bool)
        for p, _ in cov:
            p = int(p); r = N0 % p
            m1 |= (P1 % p) == r; m2 |= (P2 % p) == r
        a1 += int((~m1).sum()); a2 += int((~m2).sum())
    out[c] = (a1 / len(s), a2 / len(s))
    print(f"[c6] c{c}: uncovered primes [170k,175k) {a1 / len(s):.2f} | [175k,180k) {a2 / len(s):.2f}", flush=True)
A = Bv = [out[c] for c in CH]
print(f"[c6] 491 chunks mean {np.mean([x[0] for x in A]):.2f} / {np.mean([x[1] for x in A]):.2f} | primes in the ranges {len(P1)} / {len(P2)}")

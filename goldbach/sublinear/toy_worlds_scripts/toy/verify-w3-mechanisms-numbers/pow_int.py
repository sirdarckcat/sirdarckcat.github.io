import numpy as np, math, sympy
rng = np.random.default_rng(31337)
tok = open('/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt').read().split()
assert tok[0] == 'COVER'
cov = {int(t.split(':')[0]): int(t.split(':')[1]) for t in tok[2:] if ':' in t}
rs = np.array(sorted(cov)); 
print("cover primes", len(rs), rs[0], rs[-1], "declared rows", tok[1])
odd_r = np.array([p for p in sympy.primerange(3, 464)])
assert len(odd_r) == 89 and list(odd_r) == list(rs)
rows = np.array([p for p in sympy.primerange(3, 200000)])
print("rows", len(rows))
RR = rows[:, None] % odd_r[None, :]          # rows x 89
def left(res):
    return int((~(RR == res[None, :]).any(axis=1)).sum())
covres = np.array([cov[int(r)] for r in odd_r])
print("cover on file leaves", left(covres))
p_row = 0.024287
# powers of two
vals = []
for m in range(100, 665):
    res = np.array([pow(2, m, int(r)) for r in odd_r])
    vals.append(left(res))
vals = np.array(vals)
print(f"2^m, m=100..664 ({len(vals)}): mean {vals.mean():.1f}, sd {vals.std(ddof=1):.1f} (pop sd {vals.std():.1f}), min {vals.min()} at m = {100+int(vals.argmin())}")
print("10^30 < 2^100:", 2**100 > 10**30, " 2^99 > 10^30:", 2**99 > 10**30, " 2^664 < 10^200:", 2**664 < 10**200, " 2^665 < 10^200:", 2**665 < 10**200)
# random nonzero classes
v2 = []
for t in range(3000):
    res = np.array([rng.integers(1, r) for r in odd_r])
    v2.append(left(res))
v2 = np.array(v2)
print(f"random nonzero classes (3000): mean {v2.mean():.1f}, sd {v2.std(ddof=1):.1f}, min {v2.min()}, max {v2.max()}, 1/565 quantile {np.quantile(v2, 1/565):.0f}")
v3 = []
for t in range(3000):
    res = np.array([rng.integers(0, r) for r in odd_r])
    v3.append(left(res))
v3 = np.array(v3)
print(f"random classes incl. zero (3000): mean {v3.mean():.1f}, sd {v3.std(ddof=1):.1f}, min {v3.min()}, max {v3.max()}")
print(f"exponents at {p_row}: cover {1502*p_row:.1f}, mean 2^m {vals.mean()*p_row:.1f}, best {vals.min()*p_row:.1f}, diff best-cover {(vals.min()-1502)*p_row:.1f}; ln 565 = {math.log(565):.2f}")
for L in (12, 60, 180, 360, 660):
    pin = [int(r) for r in odd_r if (pow(2, L, int(r)) == 1)]
    print(f"L = {L}: pins {len(pin)} primes, ln product {sum(math.log(r) for r in pin):.1f}, price L ln 2 = {L*math.log(2):.1f}")

import math, random
import numpy as np
from sympy import primerange, n_order, factorint, jacobi_symbol
rs = list(primerange(3, 464)); PR = np.array(list(primerange(3, 200000)), dtype=np.int64)
print(len(rs), len(PR))
# cover file
line = open("/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt").read().split()
print(line[:3], len(line))
cl = {}
for tok in line:
    if ':' in tok:
        r, a = tok.split(':'); cl[int(r)] = int(a)
def left_cl(c):
    alive = np.ones(len(PR), bool)
    for r in rs: alive &= (PR % r) != c[r]
    return int(alive.sum())
if all(r in cl for r in rs): print("cover rows left (odd primes<200000 in no class):", left_cl(cl))
v = []
for m in range(100, 665):
    v.append((left_cl({r: pow(2, m, r) for r in rs}), m))
vv = [t[0] for t in v]
print("2^m m=100..664: n=%d mean %.1f sd %.1f min %s" % (len(v), np.mean(vv), np.std(vv), min(v)))
print("2^100 > 10^30:", 2**100 > 10**30, " 2^664 < 10^200:", 2**664 < 10**200, " 2^665 < 10^200:", 2**665 < 10**200, "2^99>10^30", 2**99 > 10**30)
random.seed(1)
rz = [left_cl({r: random.randrange(1, r) for r in rs}) for _ in range(1500)]
print("random nonzero classes: mean %.1f sd %.1f min %d" % (np.mean(rz), np.std(rz), min(rz)))
for L in (12, 60, 180, 360, 660):
    pr = [r for r in rs if L % n_order(2, r) == 0]
    print(L, len(pr), "%.1f" % sum(math.log(r) for r in pr), "%.1f" % (L*math.log(2)))
# Prop 6 (ii)
bad = 0; tot = 0
ps = list(primerange(3, 400))
for _ in range(5000):
    kk = random.randint(1, 6); fs = random.sample(ps, kk); n = math.prod(fs); nd = sum(n//r for r in fs)
    k3 = sum(1 for r in fs if r % 4 == 3)
    tot += 1; bad += jacobi_symbol(nd % n, n) != (-1)**(k3*(k3-1)//2)
print("Jacobi(n'|n) rule:", tot, bad)

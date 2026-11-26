import sys, math, numpy as np, gmpy2
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
F = cr.S + "q200000_m89.txt"
def cover():
    l = [x for x in open(F) if x.startswith(("COVER", "BEST"))][0].split()
    return [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
def setup(Q=200000):
    cov = cover()
    rows, p = cr.load(F); rows = rows[rows < Q]
    M = 2
    for r, _ in cov: M *= r
    # CRT, even
    N0 = 0; mod = 2
    for r, a in cov:
        t = ((a - N0) * pow(mod, -1, r)) % r
        N0 += t * mod; mod *= r
    assert mod == M and N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
    X = 10 ** 200
    K = (X - 1 - N0) // M + 1          # members N0 + k M < 10^200, k = 0..K-1
    return cov, rows, N0, M, K
if __name__ == "__main__":
    cov, rows, N0, M, K = setup()
    print(len(cov), len(rows), K, math.log2(K), math.log(M) / math.log(10))
    with open("params.txt", "w") as f:
        f.write(f"{N0:x}\n{M:x}\n{K}\n{len(rows)}\n" + " ".join(map(str, rows)) + "\n" + " ".join(str(r) for r, _ in cov) + "\n")

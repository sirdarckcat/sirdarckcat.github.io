# Theorem 4 (i),(ii): linear-algebraic folded-RS interpolation Q = A_0(X) + sum_{j=1..s} A_j(X) Y_j,
# deg A_j <= D-1 (j>=1), deg A_0 <= D+k-2; conditions at X = g^(i m + j), j = 0..m-s, for each listed m-tuple.
import random, itertools
from flint import nmod_mat, nmod_poly
def primitive_root(q):
    for g in range(2, q):
        x = 1; ok = True
        for e in range(1, q - 1):
            x = x * g % q
            if x == 1: ok = False; break
        if ok: return g
def kernel_dim(q, m, s, Npos, k, D, lists):
    g = primitive_root(q)
    rows = []
    for i in range(Npos):
        for j in range(m - s + 1):
            a = pow(g, i * m + j, q)
            windows = set(tuple(t[j:j + s]) for t in lists[i])
            for wv in windows:
                r = [pow(a, e, q) for e in range(D + k - 1)]
                for y in wv:
                    r += [y * pow(a, e, q) % q for e in range(D)]
                rows.append(r)
    ncol = (s + 1) * D + k - 1
    Mx = nmod_mat(len(rows), ncol, [x for r in rows for x in r], q)
    return ncol - Mx.rank(), len(rows), ncol
rng = random.Random(5)
tot = 0; zero = 0; nz_planted = 0; tot_planted = 0
for q, m, Npos in ((31, 3, 10), (31, 5, 6), (61, 4, 15), (61, 6, 10), (127, 6, 21)):
    g = primitive_root(q)
    for s in range(1, m + 1):
        W = Npos * (m - s + 1)
        for k in (2, 3, 5, 8):
            f = [rng.randrange(q) for _ in range(k)]
            F = nmod_poly(f, q)
            code = [tuple(int(F(pow(g, i * m + j, q))) for j in range(m)) for i in range(Npos)]
            for D in sorted(set([1, 2, max(1, (W - k + 1) // 2), max(1, W - k + 1)])):
                if D + k - 1 > W: continue
                # (ii) product lists with two values per coordinate, containing the codeword
                for trial in range(3):
                    lists = []
                    for i in range(Npos):
                        axes = [(code[i][j], (code[i][j] + rng.randrange(1, q)) % q) for j in range(m)]
                        lists.append(list(itertools.product(*axes)))
                    kd, nr, nc = kernel_dim(q, m, s, Npos, k, D, lists)
                    tot += 1; zero += (kd == 0)
            # (i) arbitrary correlated lists of l <= s tuples containing the codeword, at the count threshold
            for l in range(1, s + 1):
                if (s + 1 - l) * W > s * (k - 1):
                    Dm = W - k + 1
                    lists = [[code[i]] + [tuple(rng.randrange(q) for _ in range(m)) for _ in range(l - 1)] for i in range(Npos)]
                    kd, nr, nc = kernel_dim(q, m, s, Npos, k, Dm, lists)
                    tot_planted += 1; nz_planted += (kd > 0)
print(f"(ii) product lists, 2 values per coordinate, codeword inside: kernel = 0 in {zero}/{tot} interpolation spaces with D+k-1 <= W")
print(f"(i) correlated lists of l <= s tuples with (s+1-l)W > s(k-1), D = W-k+1: kernel nonzero in {nz_planted}/{tot_planted}")

# independent python-flint recomputation of G, D (no sieve) for small instances, and of parity/thresholds
import sys, flint, itertools
def field(q):
    if q == 9:
        F = flint.fq_default_ctx(3, 2, var="i", modulus=flint.fmpz_mod_poly_ctx(3)([1,0,1]))
        els = [F([a, b]) for b in range(3) for a in range(3)]   # label a+3b
        R = flint.fq_default_poly_ctx(F)
    else:
        F = flint.fq_default_ctx(q, 1)
        els = [F(a) for a in range(q)]
        R = flint.fq_default_poly_ctx(F)
    return F, els, R
def poly(R, els, q, v, d):
    c = []
    for _ in range(d): c.append(els[v % q]); v //= q
    c.append(els[1]); return R(c)
def allG(q, n):
    F, els, R = field(q)
    rows = []; rb = [0]
    for d in range(1, n):
        for v in range(q ** d):
            P = poly(R, els, q, v, d)
            if P.is_irreducible(): rows.append((d, P))
        rb.append(len(rows))
    out = []
    for v in range(q ** n):
        N = poly(R, els, q, v, n); G = len(rows); D = n
        for i, (d, Q) in enumerate(rows):
            if (N - Q).is_irreducible(): G = i; D = d; break
        out.append((G, D))
    return out, rows
if __name__ == "__main__":
    q, n = int(sys.argv[1]), int(sys.argv[2])
    out, rows = allG(q, n)
    import collections
    gh = collections.Counter(g for g, d in out); dh = collections.Counter(d for g, d in out)
    # compare with venum output
    my = {}; myd = {}
    for line in open(f"out/v_{q}_{n}.txt"):
        t = line.split()
        if t[0] == "GH": my[int(t[1])] = int(t[2])
        if t[0] == "DH": myd[int(t[1])] = int(t[2])
    print(q, n, "G hist equal:", my == dict(gh), "D hist equal:", myd == dict(dh), "Gmax", max(gh), "count", gh[max(gh)])
    import numpy as np, os
    fn = f"out/v_{q}_{n}.g16"
    if os.path.exists(fn):
        g = np.fromfile(fn, dtype=np.uint16)
        print("  per-N G identical:", all(int(g[v]) == out[v][0] for v in range(q ** n)))

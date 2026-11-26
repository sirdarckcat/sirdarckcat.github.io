# Exhaustive window of g(N), N even, N in [N0, N0 + 2L).
# g(N) = least odd prime q with N - q prime.  Also stores, for every integer m in the window
# [N0 - GMAX, N0 + 2L): isprime(m) and spf(m) = smallest prime factor if <= 65521, else 0.
# usage: python3 gdata.py N0 L name      -> data/<name>_{g,isp,spf}.npy, data/<name>.json
import sys, math, json, time, os
import numpy as np

GMAX = 40000          # rows q < GMAX (far above any g in these ranges)
SPF_CAP = 65521       # largest prime below 2^16

def primes_upto(n):
    """odd-only sieve; returns int64 array of primes <= n"""
    if n < 2: return np.array([], dtype=np.int64)
    m = (n - 1) // 2                     # index i <-> 2i+1, i = 0..m
    s = np.ones(m + 1, dtype=bool); s[0] = False
    for i in range(1, (math.isqrt(n) - 1) // 2 + 1):
        if s[i]:
            p = 2 * i + 1
            s[(p * p - 1) // 2::p] = False
    return np.concatenate([np.array([2], dtype=np.int64), 2 * np.nonzero(s)[0].astype(np.int64) + 1])

def build(N0, L):
    t0 = time.time()
    N0 -= N0 % 2
    lo, hi = N0 - GMAX, N0 + 2 * L
    W = hi - lo
    isp = np.ones(W, dtype=bool)
    spf = np.zeros(W, dtype=np.uint16)
    P = primes_upto(math.isqrt(hi) + 1)
    small = P[P <= W]; large = P[P > W]
    for p in small:                                   # increasing order: first write wins in spf
        p = int(p); st = (-lo) % p
        isp[st::p] = False
        if p <= SPF_CAP:
            v = spf[st::p]; v[v == 0] = p
    for chunk in np.array_split(large, max(1, large.size // 5_000_000)):
        st = (-(lo % chunk)) % chunk
        isp[st[st < W]] = False
    rows = P[(P >= 3) & (P < GMAX)]
    g = np.zeros(L, dtype=np.int32); un = np.arange(L, dtype=np.int64)
    base = N0 - lo
    for q in rows:
        hit = isp[base - int(q) + 2 * un]
        g[un[hit]] = q; un = un[~hit]
        if un.size == 0: break
    assert un.size == 0, "GMAX too small"
    return dict(N0=N0, L=L, lo=lo, hi=hi, GMAX=GMAX, SPF_CAP=SPF_CAP, seconds=round(time.time() - t0, 1)), g, isp, spf

if __name__ == "__main__":
    N0 = int(float(sys.argv[1])); L = int(float(sys.argv[2])); name = sys.argv[3]
    os.makedirs("data", exist_ok=True)
    meta, g, isp, spf = build(N0, L)
    np.save(f"data/{name}_g.npy", g); np.save(f"data/{name}_isp.npy", isp); np.save(f"data/{name}_spf.npy", spf)
    meta.update(gmax_found=int(g.max()), N_at_max=int(meta["N0"] + 2 * int(g.argmax())), mean_g=float(g.mean()),
                primes_in_window=int(isp.sum()))
    json.dump(meta, open(f"data/{name}.json", "w"))
    print(json.dumps(meta))

import json, math
import numpy as np

DATA = "data"

def load(name):
    meta = json.load(open(f"{DATA}/{name}.json"))
    g = np.load(f"{DATA}/{name}_g.npy")
    isp = np.load(f"{DATA}/{name}_isp.npy", mmap_mode="r")
    spf = np.load(f"{DATA}/{name}_spf.npy", mmap_mode="r")
    return meta, g, isp, spf

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, math.isqrt(n) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

def rows_below(G):
    p = primes_upto(G); return p[(p >= 3) & (p < G)]

def rough(spf, z):
    """window numbers with no prime factor <= z (spf == 0: none <= 65521)"""
    s = np.asarray(spf)
    return (s == 0) | (s > z)

def row_view(arr, meta, q, L=None):
    """arr[N - q] for N = N0 + 2i, i = 0..L-1"""
    L = meta["L"] if L is None else L
    a = meta["N0"] - meta["lo"] - int(q)
    return arr[a:a + 2 * L:2][:L]

def count_rows(arr, meta, qs, L=None):
    L = meta["L"] if L is None else L
    u = np.zeros(L, dtype=np.int16)
    for q in qs:
        u += row_view(arr, meta, q, L)
    return u

def thresholds(g, pcts=(1.0, 0.1, 0.01)):
    return [int(np.percentile(g, 100 - p)) + 1 for p in pcts]

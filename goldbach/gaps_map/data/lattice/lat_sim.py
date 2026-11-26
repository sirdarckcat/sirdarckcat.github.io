import numpy as np, math, sys, time
import os
ROWS = os.path.dirname(os.path.abspath(__file__)) + '/'
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]; cls = np.load(ROWS + 'cls_sa_11.npy'); alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; n = len(R)
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1; K = int(float(sys.argv[2])) if len(sys.argv) > 2 else 20_000_000; z = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
rng = np.random.default_rng(seed); ss = [int(s) for s in primes_upto(z) if s > 463]
print('rows', n, 'window K = %.1e (ln K = %.2f), primes (463, %d]: %d' % (K, math.log(K), z, len(ss)), flush=True)
dh = np.zeros(K, dtype=np.float32); dsft = np.zeros(K, dtype=np.float32); kk = np.arange(K, dtype=np.int64); t0 = time.time()
mh = vh = ms = vs = 0.0
for s in ss:
    c = np.bincount(R % s, minlength=s).astype(np.float32); lns = np.float32(math.log(s))
    a = int(rng.integers(s)); m = int(rng.integers(1, s)); idx = ((a + (kk % s) * m) % s).astype(np.int32)
    dh += lns * (c[idx] >= 1); dsft += lns * c[idx]
    h = (c >= 1).astype(float); mh += math.log(s) * h.mean(); vh += math.log(s) ** 2 * h.var(); ms += math.log(s) * c.mean(); vs += math.log(s) ** 2 * c.var()
print('simulated in %.0f s' % (time.time() - t0))
for name, d, mu, var in (('hard (agreement ln-weight, e = 1)', dh, mh, vh), ('soft (row counts as weights)', dsft, ms, vs)):
    d = d.astype(np.float64); print('%s: predicted mean %.1f sd %.1f ; simulated mean %.1f sd %.1f ; max %.1f = mean + %.2f sd ; top five: %s' % (name, mu, math.sqrt(var), d.mean(), d.std(), d.max(), (d.max() - d.mean()) / d.std(), np.round(np.sort(d)[-5:], 0).tolist()))
    print('   Gaussian expectation for the maximum of %.0e draws: +%.2f sd; members above mean + 4 sd: %d (Gaussian %.0f); above + 5 sd: %d (Gaussian %.1f)' % (K, math.sqrt(2 * math.log(K)) - (math.log(math.log(K)) + math.log(4 * math.pi)) / (2 * math.sqrt(2 * math.log(K))), int((d > d.mean() + 4 * d.std()).sum()), K * 3.17e-5, int((d > d.mean() + 5 * d.std()).sum()), K * 2.87e-7))

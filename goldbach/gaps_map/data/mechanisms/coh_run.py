import numpy as np, sys, math, subprocess, os, time
sys.path.insert(0, '.')
from lib import *
cfg = {'A': (10**9, 1000), 'B': (2 * 10**9, 1000), 'C': (10**9, 900)}
dt = np.dtype([('idx', '<u4'), ('k1', 'u1'), ('k199', 'u1'), ('f23', 'u1'), ('f199', 'u1'), ('coh', 'u1'), ('s', 'u1'), ('p0', 'u1'), ('p1', 'u1')])
res = {}
for nm in sys.argv[1:]:
    X, Q = cfg[nm]; m = Mini(nm); k1 = np.asarray(m.k[:, 0]); s = np.asarray(m.s)
    succ_k1 = k1[s == 1]; srt = np.sort(succ_k1); k1max = int(srt[int(0.92 * len(srt))])
    sel = np.flatnonzero(k1 <= k1max); print(nm, 'k1max', k1max, 'subset', len(sel), 'successes in subset', int(s[sel].sum()), flush=True)
    np.asarray(m.idx[sel], dtype=np.uint32).tofile(f'coh_{nm}.u32'); t0 = time.time()
    subprocess.run(['./evalN', str(X), str(Q), f'coh_{nm}.u32', f'coh_{nm}.out'], check=True, env=dict(os.environ, OMP_NUM_THREADS='4')); print('evalN', round(time.time() - t0), 's', flush=True)
    r = np.fromfile(f'coh_{nm}.out', dtype=dt); K1 = 64; NC = 12
    key = r['k1'].astype(np.int64) * NC + np.minimum(r['coh'].astype(np.int64), NC - 1)
    counts = np.bincount(key, minlength=K1 * NC); sc = np.bincount(key[r['s'] == 1], minlength=K1 * NC); sk = key[r['s'] == 1]
    kk = np.arange(K1 * NC) // NC; cc = np.arange(K1 * NC) % NC
    # distribution of coh among members and among successes
    tot = counts.reshape(K1, NC).sum(0); st = sc.reshape(K1, NC).sum(0)
    print(' coh distribution members', np.round(tot / tot.sum(), 4).tolist()); print(' coh distribution successes', np.round(st / max(st.sum(), 1), 4).tolist())
    # k1-reweighted comparison of mean coh
    pk = counts.reshape(K1, NC); ps = sc.reshape(K1, NC); w = ps.sum(1) / np.maximum(pk.sum(1), 1)
    mean_c_ctrl = (pk * cc[:NC][None, :] * w[:, None]).sum() / (pk.sum(1) * w).sum(); mean_c_succ = (ps * cc[:NC][None, :]).sum() / ps.sum()
    print(' mean coh: successes %.3f vs k1-matched members %.3f' % (mean_c_succ, mean_c_ctrl))
    sig_b = kk.astype(float); sig_m = kk * 100.0 - cc
    pt, bs, pb, pm = gain_boot(counts, sc, sk, sig_b, sig_m, B=200)
    print(' ordering by (k1, -coh):', fmt(pt, bs), flush=True)
    # also a mild variant: coh counted only if >= 3 etc is covered by the same table; and the predicted-mass test

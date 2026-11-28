import subprocess, sys, os, math, re, numpy as np
sys.path.insert(0, '.')
from lib import *
X = 2000000000
for Q in [int(v) for v in sys.argv[1:]]:
    pre = f'Q{Q}'
    if not os.path.exists(pre + '.s.u8'):
        r = subprocess.run(['./mini', str(X), str(Q), pre], capture_output=True, text=True); print(r.stdout.strip(), flush=True)
    m = Mini(pre); k1 = np.asarray(m.k[:, 0]).astype(np.int64); s = np.asarray(m.s)
    nrows = int(np.asarray(m.k[:, 0]).max()) + 0  # placeholder
    srt = np.sort(k1[s == 1]); tot = len(srt)
    # rows = pi(Q)-1 (odd primes below Q)
    sieve = np.ones(Q, bool); sieve[:2] = False
    for i in range(2, int(Q ** .5) + 1):
        if sieve[i]: sieve[i * i::i] = False
    rows = int(sieve.sum()) - 1; cmin = int(round(0.30 * rows))
    ks = sorted(set([int(srt[int(0.12 * tot)]), int(srt[int(0.25 * tot)])]))
    print(f'Q={Q}: successes {tot}, rows {rows}, cmin {cmin}, kmax candidates {ks}', flush=True)
    del m, k1, s
    subprocess.run(['python3', 'nbr4_drive.py', pre, str(X), str(Q), ','.join(map(str, ks)), '5', str(cmin)], check=False)
    # free disk of big files after use
    for ext in ('idx.u32', 'k.u8', 's.u8'): os.remove(f'{pre}.{ext}')

import json, math, time, sys
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from sympy import primerange

spec = json.load(open('goldbach/phd/campaign3/base_spec.json'))
moduli = [int(r) for r, a in spec['cover']]
boost = float(spec['boost']); LNN = 199*math.log(10)

def lp_bound(Q):
    t0 = time.time()
    P = np.array(list(primerange(3, Q)), dtype=np.int64)
    nP = len(P)
    offs, tot = {}, 0
    for r in moduli:
        offs[r] = tot; tot += r
    ncols = tot + nP
    rows, cols, vals = [], [], []
    for i, r in enumerate(moduli):
        res = (P % r).astype(np.int64)
        rows.extend(range(nP)); cols.extend(offs[r] + res); vals.extend([-1.0]*nP)
    rows.extend(range(nP)); cols.extend(range(tot, tot+nP)); vals.extend([1.0]*nP)
    rbase = nP
    for i, r in enumerate(moduli):
        rows.extend([rbase+i]*r); cols.extend(range(offs[r], offs[r]+r)); vals.extend([1.0]*r)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(nP+len(moduli), ncols))
    b = np.concatenate([np.zeros(nP), np.ones(len(moduli))])
    c = np.zeros(ncols); c[tot:] = -1.0
    res = linprog(c, A_ub=A, b_ub=b, bounds=(0, 1), method='highs')
    cov = -res.fun
    minU = nP - cov
    print(f"Q={Q}: primes={nP} LP max coverage={cov:.2f} -> min |U| >= {minU:.2f} "
          f"(E floor {minU*boost/LNN:.2f})  [{time.time()-t0:.0f}s status={res.status}]", flush=True)

for q in [int(a) for a in sys.argv[1:]] or [122000, 200000]:
    lp_bound(q)

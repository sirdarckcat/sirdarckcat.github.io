# Rows of ANY degree whose derivative is J-smooth: the parity formula applies to them too.
# N = lam * V^p (V = product of the monic irreducibles of degree <= J, optionally times x), rows Q monic
# irreducible of degree d with J + 1 < d < n.  "smooth": every root of Q' is a root of N (Q' | N^deg Q').
# For smooth rows the formula must hold in every case; for the others the parity is expected to be mixed.
#   usage: python3 -I smooth_rows.py p:J:dmax[,p:J:dmax...]
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0] if '/' in sys.argv[0] else '.')
from gen_parity_lib import *

cases = [tuple(int(v) for v in x.split(':')) for x in sys.argv[1].split(',')]
for (p, J, dmax) in cases:
    V = [1]
    for d in range(1, J + 1):
        for f in monic_irreducibles(d, p): V = mul(V, f, p)
    for lam in range(1, p):
        for extra in (0, 1):
            U = V if extra == 0 else mul(V, [0, 1], p)
            N = [1]
            for _ in range(p): N = mul(N, U, p)
            N = [x * lam % p for x in N]
            n = len(N) - 1
            for d in range(J + 2, dmax + 1):
                if d >= n: continue
                sm = [0, 0, 0]; ns = [0, 0]      # smooth: rows, r even, agree ; not smooth: rows, r even
                for Q in monic_irreducibles(d, p):
                    Qp = deriv(Q, p); e = len(Qp) - 1; l = Qp[-1]
                    smooth = (e == 0) or (powmod(N, e, Qp, p) == [])
                    f = sub(N, Q, p)
                    r = nfactors_squarefree(f, p)
                    if smooth:
                        A = n * (n - 1) // 2 + n + n * e + e + e * d + d * (d - 1) // 2
                        pred = chi(-1, p) ** A * chi(lam, p) ** (n - 2 - e) * chi(l, p) ** (n - d) * (-1) ** (d - 1)
                        sm[0] += 1; sm[1] += (r % 2 == 0); sm[2] += ((-1) ** (n - r) == pred)
                    else:
                        ns[0] += 1; ns[1] += (r % 2 == 0)
                print("p=%d J=%d lam=%d n=%d d=%d: derivative %d-smooth: %d rows, %d agree with the formula (%d with r even) | not smooth: %d rows, %d with r even" % (
                    p, J, lam, n, d, J, sm[0], sm[2], sm[1], ns[0], ns[1]))
                sys.stdout.flush()

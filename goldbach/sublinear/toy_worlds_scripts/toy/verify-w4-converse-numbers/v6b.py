import math, numpy as np, sympy, gmpy2
from vlib import *
cov, rows = get(); n = len(rows)
qnr = sum(1 for r, a in cov.items() if gmpy2.jacobi(a, r) == -1); qr = sum(1 for r, a in cov.items() if gmpy2.jacobi(a, r) == 1); z = sum(1 for r, a in cov.items() if a == 0)
print("cover classes a_r: non-residues %d, residues %d, zero %d of %d" % (qnr, qr, z, len(cov)))
print("product over r of (1 - (1+(a_r/r))/(r-1)) = %.4f ; row share prod(1-1/(r-1)) = %.4f" % (math.prod(1 - (1 + gmpy2.jacobi(a, r)) / (r - 1) for r, a in cov.items()), math.prod(1 - 1 / (r - 1) for r in cov)))
sq = [p for p in sympy.primerange(2, 448) if all((p * p) % r != a for r, a in cov.items())]
print("primes p <= 447 with p^2 in no cover class: %d of %d  -> predicted mean W = -%.1f (measured -13.1 +- 1.4 on 467..5000)" % (len(sq), sympy.primepi(447), len(sq) / 2))

# Self-checks of the sieve tables in every pass-1 file: number of monic irreducibles of degree n and of rows against the
# necklace formula; number of polynomials with mu = -1 against (q^n - q^(n-1))/2; total of the G histogram against q^n.
import glob, re
from sympy import divisors, mobius
def I(q, n): return sum(mobius(d) * q ** (n // d) for d in divisors(n)) // n
bad = 0; nfiles = 0
for fn in glob.glob("out_*_*.txt"):
    q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:]); nfiles += 1; tot = 0
    for line in open(fn):
        t = line.split()
        if t[0] == "q":
            nirr = int(t[t.index("n:") + 1]); nrows = int(t[t.index("(deg<n):") + 1])
            bad += nirr != I(q, n); bad += nrows != sum(I(q, d) for d in range(1, n))
        if t[0] == "check:": bad += int(t[3]) != (q ** n - q ** (n - 1)) // 2
        if t[0] == "GH" and int(t[1]) <= n: tot += int(t[3])
    bad += tot != q ** n
print(f"{nfiles} files checked, {bad} discrepancies")

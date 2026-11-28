import sys, sympy
sys.path.insert(0, '/home/user/sirdarckcat.github.io/goldbach/sublinear')
import cover_record as cr
rows, p = cr.load(cr.S + "q200000_m89.txt")
print(len(rows), type(p), (p if not hasattr(p,'__len__') else len(p)))
tok = open('/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt').read().split()
cov = {int(t.split(':')[0]): int(t.split(':')[1]) for t in tok[2:] if ':' in t}
mine = [q for q in sympy.primerange(3, 200000) if all(q % r != a for r, a in cov.items())]
print(len(mine), sorted(set(mine) - set(int(t) for t in rows)), sorted(set(int(t) for t in rows) - set(mine)))

# The integer shadow of Stickelberger's theorem, and why it is empty.
# F_q[x]:  chi(Res(f, f')) = product over pi | f of (f'/pi); the "self term" (pi'/pi) = chi(-1)^(d(d-1)/2) (-1)^(d-1), d = deg pi,
#          carries the parity of the NUMBER of factors, and f' is computed without factoring f.
# Z:       the only Leibniz map with n' computable from the factors is the arithmetic derivative n' = sum n/r (r' = 1).
#          For odd squarefree n = r_1...r_k:   Jacobi(n' | n) = (-1)^C(k3, 2),  k3 = #{r_i = 3 mod 4}:
#          the self term (r'/r) = (1/r) = +1 carries nothing, the cross terms are quadratic reciprocity, and n' needs the factors.
# Checked below on random squarefree products; also: Jacobi(n'|n) is not a function of the parity of k.
import random
from sympy import randprime, jacobi_symbol
from math import comb
random.seed(4); bad = 0; tab = {}
for _ in range(20000):
    k = random.randrange(1, 7); rs = set()
    while len(rs) < k: rs.add(randprime(3, 10 ** 6))
    rs = list(rs); n = 1
    for r in rs: n *= r
    nd = sum(n // r for r in rs)
    k3 = sum(1 for r in rs if r % 4 == 3)
    J = jacobi_symbol(nd % n, n)
    bad += (J != (-1) ** comb(k3, 2))
    t = tab.setdefault((k % 2, J), 0); tab[(k % 2, J)] = t + 1
print(f"Jacobi(n'|n) = (-1)^C(k3,2): 20000 random odd squarefree n with 1..6 prime factors, exceptions {bad}")
print("joint counts (k mod 2, Jacobi(n'|n)):", sorted(tab.items()))

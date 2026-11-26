import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(6)
k=2; q=4
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; zero=F(0); one=F(1)
def nfac(f): return sum(m for _, m in f.factor()[1])
L2 = (x**16 + x)*(x**4 + x)
quart = []
for c in itertools.product(els, repeat=4):
    Q = R(list(c)+[one])
    if Q.is_irreducible(): quart.append(Q)
q0 = [Q for Q in quart if Q.coeffs()[3] == zero]; q1 = [Q for Q in quart if Q.coeffs()[3] != zero]
st = Counter(); irr = Counter()
for t in range(60):
    B = R([random.choice(els) for _ in range(5)] + [one]); A = L2*B
    b1 = B.coeffs()[4]
    N = A**4
    for Q in q0:
        r = nfac(N - Q); st[('q3=0', 'b1=0' if b1 == zero else 'b1!=0', r % 2)] += 1; irr['q3=0', r == 1] += 1
    for Q in q1[:12]:
        r = nfac(N - Q); st[('q3!=0', r % 2)] += 1
print(sorted(st.items())); print(irr)
# also general A (not multiple of L): irreducible quartics q3=0
st = Counter()
for t in range(60):
    a = random.randint(3, 9)
    A = R([random.choice(els) for _ in range(a)] + [one])
    for Q in q0:
        r = nfac(A**4 - Q); st[('random A, irreducible q3=0', r % 2)] += 1
print(sorted(st.items()))

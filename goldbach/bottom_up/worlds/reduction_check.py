# W4.5: subset sum reduces to "is there k in [0, K) with k mod p_i in A_i, |A_i| = 2, for every i" (distinct primes).
# Weights w_i >= 1, target 1 <= T <= W = sum w_i. D = W + 1; distinct primes p_i > 2nD; P = prod p_i.
# v_i = round(p_i w_i / D); A_i = {0, v_i (P/p_i) mod p_i}; the window is x/P in [(T - 1/2)/D, (T + 1/2)/D).
# Check: for random instances, every class vector (all 2^n) is mapped by the CRT to x, and x lies in the window exactly when its
# subset sums to T.
#   python3 reduction_check.py > reduction_check.out
import random, math
from fractions import Fraction

def is_prime(x):
    if x < 2: return False
    d = 2
    while d * d <= x:
        if x % d == 0: return False
        d += 1
    return True

random.seed(5)
inst = agree = yes = 0
for trial in range(400):
    n = random.randint(3, 10); w = [random.randint(1, 60) for _ in range(n)]; W = sum(w)
    T = random.randint(1, W)
    D = W + 1
    ps = []; x = 2 * n * D + 1
    while len(ps) < n:
        if is_prime(x): ps.append(x)
        x += 1
    P = math.prod(ps)
    A = []
    for p, wi in zip(ps, w):
        v = (p * wi * 2 + D) // (2 * D)        # nearest integer to p w / D
        A.append((0, (v * (P // p)) % p))
    lo = Fraction(2 * T - 1, 2 * D); hi = Fraction(2 * T + 1, 2 * D)
    found_window = found_sum = False; ok = True
    for mask in range(1 << n):
        x = 0
        for i, p in enumerate(ps):
            r = A[i][(mask >> i) & 1]; e = (P // p) * pow(P // p, -1, p)
            x = (x + r * e) % P
        inwin = lo <= Fraction(x, P) < hi
        sums = sum(w[i] for i in range(n) if (mask >> i) & 1) == T
        if inwin != sums: ok = False
        found_window |= inwin; found_sum |= sums
    inst += 1; agree += ok; yes += found_sum
    K = P // D
print(f"{inst} random instances (n = 3..10 items, weights 1..60): class vectors with x in the window = subsets summing to T in "
      f"{agree} of {inst}; {yes} instances solvable")

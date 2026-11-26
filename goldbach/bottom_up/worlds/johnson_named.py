# W2.1b: what it takes to certify a set C of members that the decoder is given (weights on the members' own classes).
# With weights on C's classes at the primes 467..y and mu uniform on C, the condition of W2.1b reads
#     Lambda(y)/|C| + (1 - 1/|C|) * pair(y) >= ln K,  Lambda(y) = sum of ln Q, pair(y) = sum of ln Q/Q (pairs like random members).
# The table gives the least y for each |C|, and the weighted classes this costs (at most |C| a place).
#   python3 johnson_named.py > johnson_named.out
import math
import numpy as np

Y = 200000
s = np.ones(Y + 1, bool); s[:2] = False
for i in range(2, int(Y ** 0.5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s)[0]; P = P[P >= 467]
lnK = 16.6; K = math.exp(lnK)
lam = np.cumsum(np.log(P)); pair = np.cumsum(np.log(P) / P)
print(f"window K = e^{lnK}; given members |C|; places the primes from 467")
print("|C| | places needed | Lambda (nats) | pair term | weighted classes a member | the scan of the window, per member of the top |C|")
for C in (10, 100, 1000, 10000):
    cond = lam / C + (1 - 1 / C) * pair
    i = int(np.argmax(cond >= lnK))
    print(f"{C} | to {P[i]:,} ({i + 1}) | {lam[i]:.0f} | {pair[i]:.2f} | {i + 1} | {K / C:.3g}")

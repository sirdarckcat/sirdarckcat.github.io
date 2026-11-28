# F_4, J=2, members N = (L_2*B)^4, B monic of degree 5 (all 1024), rows of degree <= 5.
# For every member: number of irreducible N-Q over the 60 quartic rows (exact), parity of r on the 12 quartics with q_3=0.
import time, sys
from ff2 import W
w = W(2); F = w.F
L2 = w.L(2)
quart = w.irreducibles(4)
q0 = [Q for Q in quart if Q.coeffs()[3] == F(0)]
q1 = [Q for Q in quart if Q.coeffs()[3] != F(0)]
print(len(quart), len(q0), len(q1), flush=True)
hits = 0; tot_irr = 0; odd_q0 = 0; irr_q0 = 0; nB = 0
t0 = time.time()
hist = {}
for B in w.monics(5):
    N = (L2*B)**4
    c = 0
    for Q in q1:
        if (N - Q).is_irreducible(): c += 1
    for Q in q0:
        r, _ = w.nfac(N - Q)
        if r % 2: odd_q0 += 1
        if r == 1: irr_q0 += 1; c += 1
    tot_irr += c; nB += 1
    hist[c] = hist.get(c, 0) + 1
    if c == 0: hits += 1
    if nB % 128 == 0: print(nB, hits, tot_irr/nB, odd_q0, f"{time.time()-t0:.0f}s", flush=True)
import math
print(f"members {nB}; hits (no irreducible quartic row) {hits}; exponent {-math.log(hits/nB):.3f}; mean irreducible {tot_irr/nB:.3f}")
print(f"q_3=0 quartics: odd r in {odd_q0} of {12*nB}; irreducible {irr_q0}")
print("histogram", sorted(hist.items()))

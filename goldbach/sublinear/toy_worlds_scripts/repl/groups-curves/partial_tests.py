"""(b) Partial tests on real 200-digit rows that survived the sieve to 10^8 (survivors.pkl).
1. Smooth-order subgroup tests: P-1 (G_m), P+1 (norm-one torus), ECM (elliptic curve), stage 1, bound B1.
   kill = a proper or improper factor found = compositeness proved.  Cost in units of one Fermat test (squarings mod n).
   Prediction: sum over prime factors p > 10^8 of P(group order B1-smooth) = integral of rho(u)/u du from u0 = ln(10^8)/ln(B1).
"""
import pickle, math, time, sys, random, gmpy2, numpy as np
from gmpy2 import mpz, powmod, gcd
from common import setup
rows, cov, N0, M, K = setup()
S = pickle.load(open("survivors.pkl", "rb"))
comp = [N0 + k * M - q for k, q, b in S if not b]
prim = [N0 + k * M - q for k, q, b in S if b]
print(f"survivors {len(S)}: composite {len(comp)}, prime {len(prim)}")
BITS = comp[0].bit_length()
def primes_upto(B):
    s = bytearray([1]) * (B + 1); s[0:2] = b"\0\0"
    for i in range(2, int(B ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(B + 1) if s[i]]
def Eof(B):
    E = mpz(1)
    for s in primes_upto(B):
        E *= s ** int(math.log(B) / math.log(s) + 1e-12)
    return E
# Dickman rho on a grid
h = 1e-3; U = 12; ng = int(U / h) + 1; rho = np.ones(ng)
for i in range(int(1 / h) + 1, ng):
    # u rho'(u) = -rho(u-1)  -> trapezoid
    u = i * h
    rho[i] = rho[i - 1] - h * 0.5 * (rho[i - 1 - int(1 / h)] / (u - h) + rho[i - int(1 / h)] / u)
def pred(B, lo=1e8, shift=1.0):
    # integral over p from lo of rho(ln(p/shift)/ln B) dp/(p ln p)
    xs = np.linspace(math.log(lo), math.log(lo) + 60, 60001); u = np.minimum((xs - math.log(shift)) / math.log(B), U - h)
    return float(np.trapezoid(rho[(u / h).astype(int)] / xs, xs))
tF = min(sum(0 * powmod(2, n - 1, n) + 1 for n in comp[:2000]) * 0 + (lambda t: (sum(1 for n in comp[:2000] if powmod(2, n - 1, n)), time.perf_counter() - t)[1])(time.perf_counter()) for _ in range(3)) / 2000
print(f"Fermat test {tF*1e6:.1f} us; of the composites, Fermat base 2 rejects {sum(1 for n in comp if powmod(2,n-1,n)!=1)}/{len(comp)}; primes pass {sum(1 for n in prim if powmod(2,n-1,n)==1)}/{len(prim)}")
print("\nP-1 stage 1 (base 2): one exponentiation by E = lcm(1..B1), then one gcd")
print("   B1   bits(E)  cost/Fermat  kills  rate      predicted   kills per Fermat-unit   false kills on primes")
for B in (30, 100, 460, 2000, 10000, 50000):
    E = Eof(B); sub = comp if B <= 2000 else comp[:12000] if B <= 10000 else comp[:3000]
    kills = sum(1 for n in sub if gcd(powmod(2, E, n) - 1, n) > 1)
    fk = sum(1 for n in prim[:1000] if gcd(powmod(2, E, n) - 1, n) > 1)
    c = E.bit_length() / BITS
    print(f"{B:6d} {E.bit_length():8d} {c:9.3f} {kills:7d}/{len(sub)} {kills/len(sub):.5f}  {pred(B):.5f}   {kills/len(sub)/c:.5f}      {fk}")
sys.stdout.flush()
# P+1: Lucas V_E(P) mod n, P = 3 ; hit if gcd(V - 2, n) > 1.  cost 2 mulmods per bit.
def lucasV(P, E, n):
    v0, v1 = mpz(2), mpz(P)
    for b in bin(E)[2:]:
        if b == "1": v0, v1 = (v0 * v1 - P) % n, (v1 * v1 - 2) % n
        else: v0, v1 = (v0 * v0 - 2) % n, (v0 * v1 - P) % n
    return v0
print("\nP+1 stage 1 (Lucas V, seed 3; finds p with p+1 or p-1 smooth, by the sign of (5/p)): cost 2 modular mult per bit")
for B in (100, 460):
    E = Eof(B); sub = comp[:15000]
    kills = sum(1 for n in sub if gcd(lucasV(3, E, n) - 2, n) > 1)
    c = 2 * E.bit_length() / BITS
    print(f"{B:6d} {E.bit_length():8d} {c:9.3f} {kills:7d}/{len(sub)} {kills/len(sub):.5f}  {pred(B):.5f}   {kills/len(sub)/c:.5f}")
sys.stdout.flush()
# ECM stage 1, Montgomery form, Suyama sigma (group order divisible by 12)
def ecm1(n, sigma, E):
    u = (sigma * sigma - 5) % n; v = (4 * sigma) % n
    x = powmod(u, 3, n); z = powmod(v, 3, n)
    d = (16 * x * v) % n
    g = gcd(d, n)
    if g > 1: return g
    a24 = (powmod(v - u, 3, n) * (3 * u + v) * gmpy2.invert(d, n)) % n
    # ladder
    x0, z0 = x, z
    x1, z1 = x, z                                   # R0 = P
    # R1 = 2P
    def dbl(x, z):
        s = (x + z); s = s * s % n; t = (x - z); t = t * t % n; w = s - t
        return s * t % n, w * (t + a24 * w) % n
    def add(xa, za, xb, zb):
        p = (xa - za) * (xb + zb) % n; m = (xa + za) * (xb - zb) % n
        s = p + m; t = p - m
        return z0 * s * s % n, x0 * t * t % n
    x2, z2 = dbl(x1, z1)
    for b in bin(E)[3:]:
        if b == "1":
            x1, z1 = add(x2, z2, x1, z1); x2, z2 = dbl(x2, z2)
        else:
            x2, z2 = add(x2, z2, x1, z1); x1, z1 = dbl(x1, z1)
    return gcd(z1, n)
print("\nECM stage 1, one curve (Suyama, sigma = 11): about 10 modular mult per bit (6 mult + 4 squarings + 1 by a constant)")
for B, cnt in ((50, 20000), (100, 20000), (460, 6000)):
    E = Eof(B); sub = comp[:cnt]
    t = time.perf_counter(); kills = sum(1 for n in sub if ecm1(n, mpz(11), E) > 1); dt = (time.perf_counter() - t) / len(sub)
    c = 10 * E.bit_length() / BITS
    print(f"{B:6d} {E.bit_length():8d} {c:9.3f} (timed {dt/tF:.1f}) {kills:7d}/{len(sub)} {kills/len(sub):.5f}  pred(order/12 smooth) {pred(B, shift=12):.5f}   per unit {kills/len(sub)/c:.6f}")
    sys.stdout.flush()
print("\nFor comparison, per Fermat-unit of work: the Fermat test itself rejects 1.0 composite; break-even for a pre-test is a kill rate equal to its cost.")

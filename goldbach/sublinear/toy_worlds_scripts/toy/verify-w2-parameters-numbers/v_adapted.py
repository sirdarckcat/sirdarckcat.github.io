# window-adapted weights: for p > K a window of K consecutive members occupies K distinct classes mod p;
# weights confined to occupied classes give mass ln p / K per prime (uniform nu on the window) instead of ln p / p.
import numpy as np, math
def sieve(n):
    s=np.ones(n+1,dtype=bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
P=sieve(3*10**8); P=P[P>463].astype(float); lp=np.log(P)
for K in (2,16,1024,4096,2**24.35):
    lnK=math.log(K)
    gain=np.where(P<=K, lp/P, lp/K)          # mass per prime, all occupied classes weighted
    cls=np.where(P<=K, P, K)                 # weighted classes per prime
    cs=np.cumsum(gain); j=int(np.searchsorted(cs,lnK))
    tot=cls[:j+1].sum()
    print(f"K={K:.6g}: lnK={lnK:.3f}; mass from p<=K: {gain[P<=K].sum():.3f}; reached at p={int(P[j])} ({j+1} primes); weighted classes {tot:.4g} = {tot/K:.4g} per member")
# direct Minkowski check for K=2 with one prime 467, both occupied classes weighted, s=1
lnp=math.log(467)
for J in (2,3,4):
    C=2*lnp          # two classes, s(s+1)/2 = 1
    print("K=2, p=467, s=1, J=%d: need A=%.3f > ln J + C'/J + (J-1)/2 ln K = %.3f"%(J,lnp,math.log(J)+C/J+(J-1)/2*math.log(2)))

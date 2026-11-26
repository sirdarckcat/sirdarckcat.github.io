# independent implementation (verifier): places over F_q (q prime), lists, brute force, interpolation matrix
import itertools, math, random
import numpy as np
from flint import nmod_mat, nmod_poly

def polys_monic(q,d):
    for t in itertools.product(range(q),repeat=d):
        yield list(t)+[1]              # low -> high
def irreducibles(q,d):
    out=[]
    for c in polys_monic(q,d):
        f=nmod_poly(c,q)
        fac=f.factor()[1]
        if len(fac)==1 and fac[0][1]==1: out.append(c)
    return out
def xpow_table(q,mod,K):
    """rows k<K: x^k mod `mod` (monic, low->high) as length-deg vectors"""
    dg=len(mod)-1; T=np.zeros((K,dg),dtype=np.int64); v=np.zeros(dg,dtype=np.int64)
    if dg==0: return T
    v[0]=1; red=(-np.array(mod[:-1],dtype=np.int64))%q
    for k in range(K):
        T[k]=v
        top=v[-1]; v=np.roll(v,1); v[0]=0; v=(v+top*red)%q
    return T
def all_coefs(q,n):
    idx=np.arange(q**n,dtype=np.int64)
    return np.stack([(idx//q**k)%q for k in range(n)],axis=1)     # row = coefficients low->high
def residues(q,n,places):
    """R[i][N] = integer index of N mod place i (base-q digits of the residue)"""
    co=all_coefs(q,n); R=[]
    for pl in places:
        d=len(pl)-1; T=xpow_table(q,pl,n)
        r=(co@T)%q
        R.append((r@(q**np.arange(d))).astype(np.int64))
    return R
def idx2vec(q,d,i): return [(i//q**k)%q for k in range(d)]
def consistent(q,n,places,lists,R=None):
    R=R or residues(q,n,places); ok=np.ones(q**n,dtype=bool)
    for i,pl in enumerate(places):
        tab=np.zeros(q**(len(pl)-1),dtype=bool); tab[list(lists[i])]=True
        ok&=tab[R[i]]
    return np.nonzero(ok)[0]
def Mcount(n,D):
    J=(D-1)//(n-1); return (J+1)*D-(n-1)*J*(J+1)//2, J
def monomials(n,D):
    return [(a,b) for b in range(0,(D-1)//(n-1)+1) for a in range(0,D-(n-1)*b)]
def polmul_mod(q,a,b,T):
    """a,b coefficient vectors (len dg); T = xpow table with >= 2dg-1 rows"""
    full=np.convolve(a,b)%q
    return (full@T[:len(full)])%q
def interp_matrix(q,n,D,conds):
    """conds: list of (place, class_index, s). rows: for b0<s: [z^b0]Q(x,c+z) = 0 mod place^(s-b0)"""
    mons=monomials(n,D); M=len(mons); J=(D-1)//(n-1)
    col={m:i for i,m in enumerate(mons)}
    na=[D-(n-1)*b for b in range(J+1)]
    blocks=[]
    binom=[[math.comb(b,b0)%q for b0 in range(J+1)] for b in range(J+1)]
    for pl,ci,s in conds:
        d=len(pl)-1; cv=np.array(idx2vec(q,d,ci),dtype=np.int64)
        pi=nmod_poly(pl,q)
        for b0 in range(min(s,J+1)):
            e=s-b0; P=[int(x) for x in (pi**e).coeffs()]; dg=d*e
            T=xpow_table(q,P,max(D,2*dg))
            c=np.zeros(dg,dtype=np.int64); c[:d]=cv
            # multiplication-by-c matrix:  row j = x^j * c mod P
            Mc=np.stack([polmul_mod(q,T[j] ,c,T) for j in range(dg)])
            blk=np.zeros((dg,M),dtype=np.int64)
            Mk=np.eye(dg,dtype=np.int64)       # mult by c^k: v -> v@Mk
            for b in range(b0,J+1):
                rows=(T[:na[b]]@Mk)%q          # x^a c^(b-b0) mod P, a<na[b]
                c0=col[(0,b)]
                blk[:,c0:c0+na[b]]=(binom[b][b0]*rows.T)%q
                Mk=(Mk@Mc)%q
            blocks.append(blk)
        if s>J+1:   # (not used in our runs) remaining conditions vacuous on this space only if b0>J: Q_b0=0 there
            pass
    A=np.concatenate(blocks,axis=0)
    return A,mons
def kernel(q,A):
    r,c=A.shape
    Mx=nmod_mat(r,c,[int(x) for x in A.ravel()],q)
    X,nul=Mx.nullspace()
    K=np.array([[int(X[i,j]) for i in range(c)] for j in range(nul)],dtype=np.int64).reshape(nul,c)
    return K
def rank(q,A):
    r,c=A.shape
    return nmod_mat(r,c,[int(x) for x in A.ravel()],q).rank()
def common_roots(q,n,D,mons,K,cands=None):
    """all N of degree<n with Q(x,N(x))=0 for every kernel basis vector Q"""
    J=(D-1)//(n-1); na=[D-(n-1)*b for b in range(J+1)]
    Qs=[]
    for v in K:
        pos=0; L=[]
        for b in range(J+1):
            L.append(nmod_poly([int(x) for x in v[pos:pos+na[b]]],q)); pos+=na[b]
        Qs.append(L)
    cur=range(q**n) if cands is None else cands
    for L in Qs:
        nxt=[]
        for Ni in cur:
            N=nmod_poly(idx2vec(q,n,Ni),q); acc=nmod_poly([0],q)
            for b in range(J,-1,-1): acc=acc*N+L[b]
            if acc.is_zero(): nxt.append(Ni)
        cur=nxt
        if not cur: break
    return sorted(cur)
def rand_lists(rng,q,places,ells,planted=None,R=None):
    lists=[]
    for i,pl in enumerate(places):
        Q=q**(len(pl)-1)
        if planted is None: lists.append(sorted(rng.sample(range(Q),ells[i])))
        else:
            c=int(R[i][planted]); others=[x for x in range(Q) if x!=c]
            lists.append(sorted([c]+rng.sample(others,ells[i]-1)))
    return lists

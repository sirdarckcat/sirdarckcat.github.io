import random, math, time, sys
from flint import fmpz_mat
rng=random.Random(4242)
def inst(q,n,m,ell):
    xs=list(range(1,m+1)); N=[rng.randrange(q) for _ in range(n)]
    ev=lambda x: sum(c*pow(x,k,q) for k,c in enumerate(N))%q
    lists=[]; tgt=[]
    for x in xs:
        v=ev(x); L=[v]+rng.sample([y for y in range(q) if y!=v],ell-1); rng.shuffle(L); lists.append(L); tgt.append(L.index(v))
    return xs,lists,tgt
def block_parasite(q,L):
    """shortest LLL vector of {d in Z^ell: sum d=0, sum d*y = 0 mod q}"""
    ell=len(L); W=1000
    rows=[[1 if j==k else 0 for j in range(ell)]+[W*1, W*L[k]] for k in range(ell)]+[[0]*ell+[0,W*q]]
    B=fmpz_mat(ell+1,ell+2,[x for r in rows for x in r]).lll()
    best=None
    for k in range(B.nrows()):
        v=[int(B[k,c]) for c in range(ell+2)]
        if v[ell]==0 and v[ell+1]==0 and any(v):
            s=sum(x*x for x in v[:ell]); best=s if best is None else min(best,s)
    return best
def attack(q,n,m,ell,xs,lists,tgt):
    r=m-n; dim=m*ell
    # GRS parity check: H[t][i] = v_i x_i^t, v_i = 1/prod_{k!=i}(x_i-x_k)
    vi=[pow(math.prod((xs[i]-xs[k])%q for k in range(m) if k!=i)%q,q-2,q) for i in range(m)]
    W2=64*m; W=4*m
    rows=[]
    for i in range(m):
        for j in range(ell):
            v=[0]*dim; v[i*ell+j]=1
            par=[]
            for t in range(r):
                a=vi[i]*pow(xs[i],t,q)*lists[i][j]%q
                if a>q//2: a-=q
                par.append(W2*a)
            bs=[0]*(m-1)
            if i==0: bs=[W]*(m-1)
            else: bs[i-1]=-W
            rows.append(v+par+bs)
    for t in range(r):
        rows.append([0]*dim+[W2*q if c==t else 0 for c in range(r)]+[0]*(m-1))
    B=fmpz_mat(len(rows),dim+r+m-1,[x for rr in rows for x in rr]).lll()
    found=False; shortest=None; par1=0
    for k in range(B.nrows()):
        v=[int(B[k,c]) for c in range(dim+r+m-1)]
        if any(v[dim:dim+r]): continue
        n2=sum(x*x for x in v)
        if n2 and (shortest is None or n2<shortest): shortest=n2
        blocks=[i for i in range(m) if any(v[i*ell:(i+1)*ell])]
        if len(blocks)==1 and not any(v[dim+r:]): par1+=1
        for sg in (1,-1):
            w=[sg*x for x in v[:dim]]
            if all(w[i*ell+tgt[i]]==1 and sum(abs(x) for x in w[i*ell:(i+1)*ell])==1 for i in range(m)): found=True
    return found,shortest,par1
for q in (257,65537):
    for ell in (2,4,5,6,8,10):
        t=time.time(); ok=0; sh=[]; pp=[]; bp=[]
        T=4
        for _ in range(T):
            xs,lists,tgt=inst(q,4,14,ell)
            f,s,p1=attack(q,4,14,ell,xs,lists,tgt); ok+=f; sh.append(s); pp.append(p1)
            if ell>2: bp.append(min(block_parasite(q,L) for L in lists))
        gh=(ell-1)*(q*q*ell)**(1/(ell-1))/(2*math.pi*math.e) if ell>2 else float('nan')
        print(f"q={q} n=4 m=14 ell={ell} dim={14*ell}: planted found {ok}/{T}; shortest reduced norm^2 {min(sh)}..{max(sh)} (target 14); single-block vectors in basis {min(pp)}..{max(pp)}; shortest single-block parasite norm^2 (LLL per block, min over blocks) {bp and (min(bp),max(bp))}; GH estimate {gh:.1f}; binom={math.comb(ell,ell//2)}; {(time.time()-t)/T:.1f}s each"); sys.stdout.flush()

import numpy as np, sys
R=int(sys.argv[1]) if len(sys.argv)>1 else 3000
B=16; L=R+B
M=2*L*L+1
sv=np.ones(M+1,bool); sv[:2]=False
for i in range(2,int(M**.5)+1):
    if sv[i]: sv[i*i::i]=False
a=np.arange(L+1,dtype=np.int64)
P=np.zeros((L+1,L+1),bool)
for i in range(1,L+1):
    P[i,1:]=sv[i*i+a[1:]**2]
rp=np.nonzero(sv[:L+1])[0]
for p in rp:
    if p%4==3: P[p,0]=True; P[0,p]=True
# Gaussian primes pi by norm, all quadrants
pis={}
for u in range(-B,B+1):
    for v in range(-B,B+1):
        m=u*u+v*v
        if m<2 or m>B*B: continue
        if P[abs(u),abs(v)]: pis.setdefault(m,[]).append((u,v))
norms=sorted(pis)
# targets
X=[];Y=[]
for y in range(0,R+1):
    xmax=int((R*R-y*y)**.5)
    x=np.arange(1,xmax+1)
    x=x[(x+y)%2==0]
    X.append(x);Y.append(np.full(len(x),y))
X=np.concatenate(X).astype(np.int32);Y=np.concatenate(Y).astype(np.int32)
grp=np.where(Y==0,0,np.where(X==Y,1,2))
g=np.zeros(len(X),np.int32)
alive=np.arange(len(X))
for m in norms:
    if len(alive)==0: break
    x=X[alive];y=Y[alive]
    hit=np.zeros(len(alive),bool)
    for (u,v) in pis[m]:
        hit|=P[np.abs(x-u),np.abs(y-v)]
    g[alive[hit]]=m
    alive=alive[~hit]
print("unresolved",len(alive))
names=['real','diagonal','generic']
print("counts",[int((grp==k).sum()) for k in range(3)])
th=[5,13,17,29,37,41,53]
for k in range(3):
    s=grp==k
    print(names[k],"alive after m=",th,[int((g[s]>m).sum()) for m in th])
    gm=g[s].max(); i=np.nonzero(s&(g==gm))[0]
    print(names[k],"max g",gm,"example",(int(X[i[0]]),int(Y[i[0]])),"count at max",len(i))

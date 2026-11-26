import sys, math, time
def primes_upto(n):
    s=bytearray([1])*(n+1); s[0:2]=b'\0\0'
    for i in range(2,int(n**0.5)+1):
        if s[i]: s[i*i::i]=bytearray(len(s[i*i::i]))
    return [i for i in range(n+1) if s[i]]
def mr(n,bases=(2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53)):
    if n<2: return False
    d=n-1; r=0
    while d%2==0: d//=2; r+=1
    for a in bases:
        if a%n==0: continue
        x=pow(a,d,n)
        if x==1 or x==n-1: continue
        for _ in range(r-1):
            x=x*x%n
            if x==n-1: break
        else: return False
    return True
N=int(open(sys.argv[1]).read().strip()); claim=int(sys.argv[2])
t=time.time()
assert N%2==0
P=primes_upto(claim+10)
g=None; prp2=0
for q in P:
    n=N-q
    if q==2: 
        assert n%2==0 and n>2; continue
    if pow(2,n-1,n)==1:
        prp2+=1
        if mr(n): g=q; break
print("digits",len(str(N)),"first q with N-q a strong probable prime (16 bases):",g,"claimed",claim,"MATCH" if g==claim else "MISMATCH","| base-2 Fermat passes seen:",prp2,"| g/ln^2N=%.4f"%(g/math.log(N)**2),"| %.1fs"%(time.time()-t))

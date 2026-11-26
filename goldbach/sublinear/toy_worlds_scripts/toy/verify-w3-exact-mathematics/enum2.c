// Verifier, second program: parity selection.  ./enum2 q n R K  -> bins (s,o) for no sieve (t=0) and sieve by first K irreducibles (t=1)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef long long ll;
int q, n; int ADD[9][9], SUB[9][9], MUL[9][9];
ll pw[40], off[40];
unsigned char *bits;
#define SETB(i) (bits[(i)>>3] |= (1u<<((i)&7)))
#define GETB(i) ((bits[(i)>>3]>>((i)&7))&1)
unsigned char *par, *nsq, *divK;   // indexed by degree-n index
static void tables(void){
  for(int a=0;a<q;a++)for(int b=0;b<q;b++){
    if(q!=9){ADD[a][b]=(a+b)%q;SUB[a][b]=((a-b)%q+q)%q;MUL[a][b]=(a*b)%q;}
    else{int a0=a%3,a1=a/3,b0=b%3,b1=b/3;
      ADD[a][b]=(a0+b0)%3+3*((a1+b1)%3); SUB[a][b]=((a0-b0)+3)%3+3*(((a1-b1)+3)%3);
      int r0=((a0*b0-a1*b1)%3+3)%3, r1=(a0*b1+a1*b0)%3; MUL[a][b]=r0+3*r1;}
  }
}
// iterate products of (not nec. monic-lower) poly A of degree dA (digits A[0..dA], A[dA]=1) with all monic b of degree db; mode 0: set composite bit; 1: flip par; 2: set nsq; 3: set divK
static void products(int *a,int da,int db,int mode){
  int b[40]; memset(b,0,sizeof b); int P[80]; memset(P,0,sizeof P);
  ll pv=0; for(int k=0;k<da;k++){P[db+k]=a[k]; pv+=(ll)a[k]*pw[db+k];}
  ll base=off[da+db]; ll cnt=pw[db];
  for(ll vb=0;;){
    if(mode==0) SETB(base+pv); else if(mode==1) par[pv]^=1; else if(mode==2) nsq[pv]=1; else divK[pv]=1;
    vb++; if(vb>=cnt) break;
    int k=0;
    for(;;){ int old=b[k], nw=(old+1==q)?0:old+1; b[k]=nw; int diff=SUB[nw][old];
      for(int j=0;j<=da;j++){ int idx=k+j; int o=P[idx]; int t=ADD[o][MUL[diff][a[j]]]; P[idx]=t; pv+=(ll)(t-o)*pw[idx]; }
      if(nw!=0) break; k++; }
  }
}
int main(int argc,char**argv){
  q=atoi(argv[1]); n=atoi(argv[2]); int R=atoi(argv[3]); int K=atoi(argv[4]); tables();
  pw[0]=1; for(int i=1;i<40;i++) pw[i]=pw[i-1]*q;
  off[0]=0; for(int i=1;i<=n+1;i++) off[i]=off[i-1]+pw[i-1];
  bits=calloc(off[n+1]/8+2,1); par=calloc(pw[n],1); nsq=calloc(pw[n],1); divK=calloc(pw[n],1);
  int a[40];
  for(int da=1; 2*da<=n; da++) for(ll va=0; va<pw[da]; va++){ if(GETB(off[da]+va)) continue;
      ll t=va; for(int k=0;k<da;k++){a[k]=t%q;t/=q;} a[da]=1;
      for(int db=da; da+db<=n; db++) products(a,da,db,0); }
  // mu at degree n
  ll seen=0;
  for(int da=1; da<=n; da++) for(ll va=0; va<pw[da]; va++){ if(GETB(off[da]+va)) continue;
      ll t=va; for(int k=0;k<da;k++){a[k]=t%q;t/=q;} a[da]=1;
      products(a,da,n-da,1);
      if(seen<K) products(a,da,n-da,3);
      seen++;
      if(2*da<=n){ // a^2
        int s[80]; memset(s,0,sizeof s);
        for(int i=0;i<=da;i++)for(int j=0;j<=da;j++) s[i+j]=ADD[s[i+j]][MUL[a[i]][a[j]]];
        products(s,2*da,n-2*da,2); } }
  ll cm=0; for(ll v=0;v<pw[n];v++) cm+=(par[v]&&!nsq[v]);
  printf("check: #mu=-1 at degree n = %lld (expect %lld)\n",cm,(pw[n]-pw[n-1])/2);
  // rows: first R irreducibles
  ll *rv=malloc(sizeof(ll)*R); int *rd=malloc(sizeof(int)*R); unsigned char *rdig=calloc((size_t)R*n,1); int r=0;
  for(int d=1;d<n&&r<R;d++) for(ll v=0;v<pw[d]&&r<R;v++) if(!GETB(off[d]+v)){rv[r]=v;rd[r]=d; ll t=v; for(int k=0;k<d;k++){rdig[r*n+k]=t%q;t/=q;} rdig[r*n+d]=1; r++;}
  static ll dl[40][9][9];
  for(int k=0;k<n;k++)for(int x=0;x<q;x++)for(int y=0;y<q;y++) dl[k][x][y]=(ll)(SUB[x][y]-x)*pw[k];
  // bins[t][s][o] : cnt, hits, tall, todd
  int W=R+1; ll *B=calloc((size_t)2*W*W*4,sizeof(ll));
  int N[40]; memset(N,0,sizeof N); ll baseN=off[n];
  for(ll v=0; v<pw[n]; v++){
    int s[2]={0,0},o[2]={0,0},ta[2]={0,0},to[2]={0,0}; int hit=1;
    for(int i=0;i<R;i++){
      int d=rd[i]; unsigned char*Q=rdig+i*n; ll w=v;
      for(int k=0;k<=d;k++) w+=dl[k][N[k]][Q[k]];
      int odd=(par[w]&&!nsq[w]); int irr=!GETB(baseN+w);
      for(int t=0;t<2;t++){ if(t==1&&divK[w]) continue; s[t]++; o[t]+=odd; if(hit){ta[t]++; to[t]+=odd;} }
      if(irr) hit=0;
    }
    for(int t=0;t<2;t++){ ll*c=B+(((size_t)t*W+s[t])*W+o[t])*4; c[0]++; c[1]+=hit; c[2]+=ta[t]; c[3]+=to[t]; }
    for(int k=0;k<n;k++){ if(++N[k]<q) break; N[k]=0; }
  }
  for(int t=0;t<2;t++)for(int s=0;s<W;s++)for(int o=0;o<W;o++){ ll*c=B+(((size_t)t*W+s)*W+o)*4; if(c[0]) printf("BIN %d %d %d %lld %lld %lld %lld\n",t,s,o,c[0],c[1],c[2],c[3]); }
  return 0;
}

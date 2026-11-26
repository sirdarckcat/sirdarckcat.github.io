// Independent enumerator (verifier). Monic polys over F_q, q in {3,5,7,9}; labels 0..q-1; F_9: label a+3b = a+b*i, i^2=-1.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef long long ll;
int q, n; int ADD[9][9], SUB[9][9], MUL[9][9];
ll pw[40], off[40];
unsigned char *bits; // bit=1 => reducible (composite)
#define SETB(i) (bits[(i)>>3] |= (1u<<((i)&7)))
#define GETB(i) ((bits[(i)>>3]>>((i)&7))&1)
static void tables(void){
  for(int a=0;a<q;a++)for(int b=0;b<q;b++){
    if(q!=9){ADD[a][b]=(a+b)%q;SUB[a][b]=((a-b)%q+q)%q;MUL[a][b]=(a*b)%q;}
    else{int a0=a%3,a1=a/3,b0=b%3,b1=b/3;
      ADD[a][b]=(a0+b0)%3+3*((a1+b1)%3);
      SUB[a][b]=((a0-b0)+3)%3+3*(((a1-b1)+3)%3);
      int r0=((a0*b0-a1*b1)%3+3)%3, r1=(a0*b1+a1*b0)%3; MUL[a][b]=r0+3*r1;}
  }
}
int main(int argc,char**argv){
  q=atoi(argv[1]); n=atoi(argv[2]); tables();
  pw[0]=1; for(int i=1;i<40;i++) pw[i]=pw[i-1]*q;
  off[0]=0; for(int i=1;i<=n+1;i++) off[i]=off[i-1]+pw[i-1];  // id of monic deg m index v = off[m]+v
  ll total=off[n+1];
  bits=calloc(total/8+2,1);
  // sieve
  for(int da=1; 2*da<=n; da++){
    for(ll va=0; va<pw[da]; va++){
      if(GETB(off[da]+va)) continue;
      int a[40]; {ll t=va; for(int k=0;k<da;k++){a[k]=t%q;t/=q;} a[da]=1;}
      for(int db=da; da+db<=n; db++){
        int b[40]; memset(b,0,sizeof b);
        int P[80]; memset(P,0,sizeof P);
        // product of a and x^db : digits (non-leading) P[db+k]=a[k], k<da
        ll pv=0; for(int k=0;k<da;k++){P[db+k]=a[k]; pv+= (ll)a[k]*pw[db+k];}
        ll base=off[da+db];
        ll cnt=pw[db];
        for(ll vb=0;;){
          SETB(base+pv);
          vb++; if(vb>=cnt) break;
          int k=0;
          for(;;){
            int old=b[k], nw=(old+1==q)?0:old+1; b[k]=nw;
            int diff=SUB[nw][old];
            for(int j=0;j<=da;j++){ int idx=k+j; int o=P[idx]; int t=ADD[o][MUL[diff][a[j]]]; P[idx]=t; pv+=(ll)(t-o)*pw[idx]; }
            if(nw!=0) break; k++;
          }
        }
      }
    }
  }
  // check counts of irreducibles
  ll Icount[40];
  for(int d=1;d<=n;d++){ ll c=0; for(ll v=0;v<pw[d];v++) c+=!GETB(off[d]+v); Icount[d]=c; }
  // rows
  ll nrows=0; for(int d=1;d<n;d++) nrows+=Icount[d];
  ll *rv=malloc(sizeof(ll)*nrows); unsigned char *rd=malloc(nrows);
  ll r=0; for(int d=1;d<n;d++) for(ll v=0;v<pw[d];v++) if(!GETB(off[d]+v)){rv[r]=v;rd[r]=d;r++;}
  // only keep rows up to a cap of degree for memory of digits: store digits packed
  unsigned char *rdig=malloc((size_t)nrows*(n)); 
  for(ll i=0;i<nrows;i++){ ll t=rv[i]; int d=rd[i]; for(int k=0;k<d;k++){rdig[i*n+k]=t%q;t/=q;} rdig[i*n+d]=1; }
  // subtraction index delta table: dl[k][Nk][Qk] = (SUB[Nk][Qk]-Nk)*q^k
  static ll dl[40][9][9];
  for(int k=0;k<n;k++)for(int x=0;x<q;x++)for(int y=0;y<q;y++) dl[k][x][y]=(ll)(SUB[x][y]-x)*pw[k];
  ll Gmax=-1,Gcnt=0,G2=-1; ll Dh[40]; memset(Dh,0,sizeof Dh); ll exc=0; double sumG=0;
  ll *Gh=calloc(nrows+2,sizeof(ll));
  int N[40]; memset(N,0,sizeof N);
  ll baseN=off[n];
  #define TOPK 8
  ll topG[TOPK], topV[TOPK]; for(int i=0;i<TOPK;i++){topG[i]=-1;topV[i]=-1;}
  for(ll v=0; v<pw[n]; v++){
    ll g=nrows; int D=n;
    for(ll i=0;i<nrows;i++){
      int d=rd[i]; unsigned char*Q=rdig+i*n; ll w=v;
      for(int k=0;k<=d;k++) w+=dl[k][N[k]][Q[k]];
      if(!GETB(baseN+w)){g=i;D=d;break;}
    }
    Gh[g]++; Dh[D]++; sumG+=g; if(g==nrows) exc++;
    if(g>topG[TOPK-1]){ int j=TOPK-1; while(j>0&&topG[j-1]<g){topG[j]=topG[j-1];topV[j]=topV[j-1];j--;} topG[j]=g;topV[j]=v; }
    // increment N digits
    for(int k=0;k<n;k++){ if(++N[k]<q) break; N[k]=0; }
  }
  for(ll g=nrows;g>=0;g--) if(Gh[g]){ if(Gmax<0){Gmax=g;Gcnt=Gh[g];} else {G2=g;break;} }
  int Dmax=0; for(int d=n;d>=1;d--) if(Dh[d]){Dmax=d;break;}
  printf("q %d n %d rows %lld Gmax %lld cnt %lld second %lld Dmax %d cnt %lld exceptions %lld meanG %.4f\n",q,n,nrows,Gmax,Gcnt,G2,Dmax,Dh[Dmax],exc,sumG/pw[n]);
  printf("  I_d:"); for(int d=1;d<=n;d++) printf(" %lld",Icount[d]); printf("\n");
  printf("  #D>=d:"); { ll c=0; ll K[40]; for(int d=n;d>=1;d--){c+=Dh[d];K[d]=c;} for(int d=2;d<=Dmax;d++) printf(" %d:%lld",d,K[d]); } printf("\n");
  printf("  top:"); for(int i=0;i<TOPK;i++) printf(" (G=%lld v=%lld)",topG[i],topV[i]); printf("\n");
  if(argc>3){ FILE*f=fopen(argv[3],"w"); for(ll g=0;g<=nrows;g++) if(Gh[g]) fprintf(f,"%lld %lld\n",g,Gh[g]); fclose(f); }
  return 0;
}

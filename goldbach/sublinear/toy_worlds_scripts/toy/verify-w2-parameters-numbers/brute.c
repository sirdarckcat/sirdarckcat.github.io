#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
// usage: brute q n m ; stdin: m lines of q 0/1 flags (list membership at point a=0..m-1)
// prints for each prefix length k=0..m the number of N (deg<n) with N(a) in L_a for a<k
int main(int argc,char**argv){ int q=atoi(argv[1]),n=atoi(argv[2]),m=atoi(argv[3]);
  static char tab[64][64]; for(int a=0;a<m;a++) for(int v=0;v<q;v++){int x; if(scanf("%d",&x)!=1) return 1; tab[a][v]=x;}
  uint64_t tot=1; for(int i=0;i<n;i++) tot*=q; uint64_t *first=calloc(m+1,sizeof(uint64_t));
  int co[16];
  for(uint64_t N=0;N<tot;N++){ uint64_t t=N; for(int k=0;k<n;k++){co[k]=t%q;t/=q;}
    int f=m; for(int a=0;a<m;a++){ int v=0; for(int k=n-1;k>=0;k--) v=(v*a+co[k])%q; if(!tab[a][v]){f=a;break;} }
    first[f]++; }
  uint64_t c=0; uint64_t *cnt=calloc(m+1,sizeof(uint64_t)); for(int k=m;k>=0;k--){c+=first[k];cnt[k]=c;}
  for(int k=0;k<=m;k++) printf("%llu ",(unsigned long long)cnt[k]); printf("\n"); return 0; }

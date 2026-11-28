#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
// segmented sieve; accumulate S(y)=sum_{467<=p<=y} ln p/p, count, sum p; report crossings of targets
int main(){
  uint64_t LIM=12000000000ULL; uint32_t sq=(uint32_t)sqrt((double)LIM)+2;
  char *sm=calloc(sq+1,1); uint32_t *pr=malloc(sizeof(uint32_t)*20000); int np=0;
  for(uint32_t i=2;i<=sq;i++){ if(!sm[i]){pr[np++]=i; for(uint64_t j=(uint64_t)i*i;j<=sq;j+=i) sm[j]=1;}}
  double targets[]={0.691,2.763,6.907,13.814,16.441,16.820,16.878}; int nt=7, ti=0;
  const uint64_t SEG=1<<22; char *seg=malloc(SEG);
  long double S=0, SP=0; uint64_t cnt=0;
  for(uint64_t lo=0; lo<LIM && ti<nt; lo+=SEG){
    memset(seg,0,SEG);
    for(int k=0;k<np;k++){ uint64_t p=pr[k]; if(p*p>=lo+SEG) break; uint64_t st=(lo+p-1)/p*p; if(st<p*p) st=p*p; for(uint64_t j=st;j<lo+SEG;j+=p) seg[j-lo]=1; }
    for(uint64_t i=0;i<SEG;i++){ uint64_t n=lo+i; if(n<467||seg[i]) continue; if(n>LIM) break;
      S+=logl((long double)n)/n; SP+=n; cnt++;
      while(ti<nt && S>=targets[ti]){ printf("mass %.3f reached at p=%llu  primes=%llu  sum p=%.4Le  (Mertens approx y=%.4e)\n",targets[ti],(unsigned long long)n,(unsigned long long)cnt,SP,463*exp(targets[ti])); fflush(stdout); ti++; }
    }
  }
  printf("end S=%.5Lf\n",S); return 0; }

// Exhaustive g(N) = least prime p with N-p prime, for every even N in [6, X].
// Output: histogram of g, running records, and every (N,g) with g >= L0 (binary: uint64 N, uint32 g).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
static uint8_t *bm; // bit i <-> odd number 2i+1
#define ISP(n) ((bm[(n)>>4] >> (((n)>>1)&7)) & 1)
int main(int argc, char **argv){
    uint64_t X = argc>1 ? strtoull(argv[1],0,10) : 4000000000ULL;
    uint32_t L0 = argc>2 ? atoi(argv[2]) : 400;
    uint64_t nb = (X>>4)+2;
    bm = malloc(nb); memset(bm,0xff,nb); bm[0] &= ~1; // 1 not prime
    uint64_t lim = (uint64_t)sqrt((double)X)+2;
    for(uint64_t i=3;i<=lim;i+=2) if(ISP(i)) for(uint64_t j=i*i;j<=X;j+=2*i) bm[j>>4] &= ~(1<<((j>>1)&7));
    // small odd primes
    static uint32_t sp[100000]; int ns=0;
    for(uint32_t i=3;i<20000 && ns<100000;i+=2) if(ISP(i)) sp[ns++]=i;
    static uint64_t hist[20000]; uint32_t rec=0;
    FILE *fo=fopen(argc>3?argv[3]:"hits.bin","wb");
    for(uint64_t N=6;N<=X;N+=2){
        uint32_t g=0;
        for(int i=0;i<ns;i++){ uint64_t m=N-sp[i]; if(ISP(m)){ g=sp[i]; break; } }
        hist[g]++;
        if(g>rec){ rec=g; printf("RECORD %llu %u\n",(unsigned long long)N,g); }
        if(g>=L0){ fwrite(&N,8,1,fo); fwrite(&g,4,1,fo); }
    }
    fclose(fo);
    FILE *fh=fopen("hist.txt","w"); for(int i=0;i<20000;i++) if(hist[i]) fprintf(fh,"%d %llu\n",i,(unsigned long long)hist[i]); fclose(fh);
    return 0;
}

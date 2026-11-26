/* sampler.c -- LD_PRELOAD statistical profiler: a SIGPROF from a 10 kHz wall-clock timer aimed at the main thread records the
 * interrupted RIP; at exit it writes "address count" lines (most frequent first) to $SAMPLER_OUT.  Meant for threads=1 on a pinned,
 * otherwise idle core.   gcc -O2 -shared -fPIC -o libsampler.so sampler.c -lrt */
#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <ucontext.h>
#include <stdint.h>
#define HSZ (1u << 20)
static timer_t tm; static uint64_t keys[HSZ]; static uint32_t cnts[HSZ]; static uint64_t total;
static void handler(int sig, siginfo_t *si, void *ctx) {
    (void)sig; (void)si;
    ucontext_t *uc = (ucontext_t *)ctx;
    uint64_t ip = uc->uc_mcontext.gregs[REG_RIP];
    uint32_t h = (uint32_t)((ip * 0x9E3779B97F4A7C15ull) >> 44) & (HSZ - 1);
    while (keys[h] && keys[h] != ip) h = (h + 1) & (HSZ - 1);
    keys[h] = ip; cnts[h]++; total++;
}
static int cmp(const void *a, const void *b) { const uint64_t *x = a, *y = b; return (y[1] > x[1]) - (y[1] < x[1]); }
static void dump(void) {
    const char *out = getenv("SAMPLER_OUT"); if (!out) out = "samples.txt";
    struct itimerspec z; memset(&z, 0, sizeof z); if (tm) timer_settime(tm, 0, &z, NULL);
    uint64_t *arr = malloc(sizeof(uint64_t) * 2 * HSZ); size_t n = 0;
    for (uint32_t i = 0; i < HSZ; i++) if (keys[i]) { arr[2*n] = keys[i]; arr[2*n+1] = cnts[i]; n++; }
    qsort(arr, n, 16, cmp);
    FILE *f = fopen(out, "w"); fprintf(f, "TOTAL %llu\n", (unsigned long long)total);
    for (size_t i = 0; i < n; i++) fprintf(f, "%llx %llu\n", (unsigned long long)arr[2*i], (unsigned long long)arr[2*i+1]);
    fclose(f);
}
__attribute__((constructor)) static void init(void) {
    struct sigaction sa; memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = handler; sa.sa_flags = SA_SIGINFO | SA_RESTART; sigaction(SIGPROF, &sa, NULL);
    struct sigevent sev; memset(&sev, 0, sizeof sev);
    sev.sigev_notify = SIGEV_THREAD_ID; sev.sigev_signo = SIGPROF; sev._sigev_un._tid = (int)syscall(SYS_gettid);
    timer_create(CLOCK_MONOTONIC, &sev, &tm);
    struct itimerspec it; it.it_interval.tv_sec = 0; it.it_interval.tv_nsec = 100000; it.it_value = it.it_interval;   /* 100 us */
    timer_settime(tm, 0, &it, NULL);
    atexit(dump);
}

#!/usr/bin/env python3
"""BatchFeeder with the bin-overflow check DEFERRED to the end of the window (BigStage.gen_group(defer=...), BatchFeeder.window: no host round trip a row group) against the per-group check,
on the CPU emulation of the kernels (test_gbatch_cpu.py's harness).  sync_every = 0 is the deferred-only mode, N >= 2 checks every N-th group on the host (a throttle for the sieve beside
the Fermat rounds), 1 (the default) is the per-group check:

  1. with the capacity the stage chose, every window is identical to the per-group path, the sticky flag stays clear, no window is repeated, and every gen_group call of the window was a deferred one
     (no per-group wait);
  2. with a capacity far too small (some bin overflows in some group) the deferred window notices the flag at the end, repeats the window the old way and returns the same window as the per-group path
     (which handles the overflow per group); the capacity has grown, so the next window is not repeated;
  3. the first, deferred attempt of such a window IS wrong (the flag is the only thing that tells): the test is not vacuous, and the tile kernel skipped the bins of the overflowed group instead of reading
     slots that were never written.

    python3 test_gbatch_defer_cpu.py
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB

FIELDS = ("k", "cnt", "offs", "rows", "alive_total", "hm_all", "hm_kept", "block")


def same(a, b):
    return all(np.array_equal(np.asarray(getattr(a, f)), np.asarray(getattr(b, f))) for f in FIELDS)


def main():
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    import gpu_sieve, gbatch, search                           # noqa: E402,F401
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec["residual"] = spec["residual"][:40]
    ok = True
    # (B, ks_log, tile_log, llog, rg, split, f, staged, rcta, stage_cap)
    for B, ks, tile, llog, rg, split, f, staged, rcta, stage_cap in ((32768, 15, 12, 11, 4, 4096, 0.9, False, 2, 8192), (32768, 15, 12, 11, 4, 4096, 0.9, True, 2, 512),
                                                                      (20011, 14, 11, 11, 3, 2048, 0.5, True, 4, 256)):
        def make():
            search.G.clear(); search._SIEVE_CACHE.clear()
            search.init_spec(spec, B, 1 << llog)
            return gbatch.BatchFeeder.from_search_G(search.G, ks_log=ks, tile_log=tile, llog=llog, f=f, nthreads=64, split=split, rg=rg, ppt=2,
                                                    gen_threads=max(32, -(-rcta * (1 << (ks - tile)) // 32) * 32), tile_threads=64, staged=staged, rcta=rcta, stage_cap=stage_cap)
        old, new = make(), make()
        old.sync_every = 1
        new.sync_every = 0
        calls = []                                              # the `defer` argument of every gen_group call of `new`
        real = new.big.gen_group
        new.big.gen_group = lambda row0, nrows, timings=None, U=None, defer=None: (calls.append(defer is not None), real(row0, nrows, timings, U, defer))[1]
        tag = f"B={B} batch 2^{ks} tile 2^{tile} rg={rg} ({new.n_small} small + {new.n_large} large primes){' staged rcta ' + str(rcta) + ' stage ' + str(stage_cap) if staged else ''}"
        # 1. normal capacity
        good = True
        for k0 in (1 << ks, 3 << ks, 2 ** 31 + (1 << ks)):
            calls.clear()
            wn, wo = new.window(k0), old.window(k0)
            good &= same(wn, wo) and all(calls) and len(calls) == -(-new.nU // rg) and new.window_retries == 0 and int(new._ovf[0]) == 0
        print(f"  {tag}: capacity {new.big.cap}: deferred check identical to the per-group check, {len(calls)} group launches a window without a wait, no repeated window: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
        # 2. forced overflow
        k0 = 5 << ks
        new.big.cap = old.big.cap = 32
        calls.clear()
        wn, wo = new.window(k0), old.window(k0)
        retried = new.window_retries
        grew = new.big.cap > 32
        good = same(wn, wo) and retried == 1 and grew and calls[0] is True and not all(calls)
        calls.clear()
        wn2, wo2 = new.window(k0 + (1 << ks)), old.window(k0 + (1 << ks))
        good &= same(wn2, wo2) and new.window_retries == 1 and all(calls)
        print(f"  {tag}: forced overflow (capacity 32): the deferred window repeated once ({retried}) with the capacity grown to {new.big.cap}, identical to the per-group path; the next window "
              f"deferred and not repeated: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
        # 3. the first attempt is wrong, and says so
        new.big.cap = 32
        new._ovf[:] = 0
        new._defer = new._ovf
        wbad = gpu_sieve.GpuFeeder.window(new, k0 + (2 << ks))
        new._defer = None
        flag = int(new._ovf[0])
        wref = old.window(k0 + (2 << ks))
        good = flag == 1 and not same(wbad, wref)
        print(f"  {tag}: the unrepeated deferred attempt of an overflowed window: flag {flag}, wrong window ({not same(wbad, wref)}): {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
        # 4. the hybrid: every 3rd group checked by the host, the others deferred; also with a forced overflow (the checked groups grow the capacity, the deferred ones before them are caught by the flag);
        #    and a group delay (a bubble) changes nothing
        hyb = make()
        hyb.sync_every = 3
        hyb.group_delay = 1e-6
        hcalls = []
        hreal = hyb.big.gen_group
        hyb.big.gen_group = lambda row0, nrows, timings=None, U=None, defer=None: (hcalls.append(defer is None), hreal(row0, nrows, timings, U, defer))[1]
        k1 = 7 << ks
        wh, wo1 = hyb.window(k1), old.window(k1)
        ngr = -(-hyb.nU // rg)
        want = [(g + 1) % 3 == 0 for g in range(ngr)]
        good = same(wh, wo1) and hcalls == want and hyb.window_retries == 0
        hcalls.clear()
        hyb.big.cap = old.big.cap = 32
        wh2, wo2 = hyb.window(k1 + (1 << ks)), old.window(k1 + (1 << ks))
        good &= same(wh2, wo2) and hyb.window_retries == 1
        print(f"  {tag}: hybrid (every 3rd group checked): {sum(want)} of {ngr} groups checked, identical, forced overflow repeated once: {'ok' if good else 'FAILED'}", flush=True)
        ok &= good
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

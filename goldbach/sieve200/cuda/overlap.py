"""Helpers for a search_gpu5-style driver: run the sieve in a thread on its own CUDA stream while the caller tests the previous window's pool, and an exact-key LRU cache.

    from overlap import overlapped, LruCache
    for item in overlapped(cp, generator):      # generator: the sieve, e.g. yields (slice index, window); items come back in order
        ...                                     # the Fermat rounds of the pool run here, on the caller's stream, while the thread sieves the next window

How it fits the GPU: the thread's stream is non-blocking (so the default stream does not wait for it) and has the highest priority (its CTAs are placed first when a Fermat CTA retires; the
Fermat kernels fill every SM, ~1 ms a CTA).  Memory hazards: cupy's pool keeps a free list per stream, so an array made in the sieve thread goes back to the sieve stream's list when it is
dropped, wherever that happens; the CALLER must therefore synchronize its own stream before it drops an array that its kernels were reading (search_gpu5's flush and window loop do).
One item waits in the queue at a time (the sieve runs at most one window ahead of the consumer, plus the one being consumed).  Errors in the thread are re-raised in the caller.
"""
import collections
import os
import queue
import threading
import time

_STREAM = {}


def new_stream(cp, priority=-100, what="sieve"):
    """a new non-blocking stream of the given priority (-100: outside every device's range [-5 .. 0], the driver clamps it to the greatest priority; 0: the default, the lowest; cupy has no
    wrapper of cudaDeviceGetStreamPriorityRange, only of cudaStreamCreateWithPriority); a plain non-blocking stream if the priority calls are missing"""
    try:
        return cp.cuda.ExternalStream(cp.cuda.runtime.streamCreateWithPriority(1, int(priority)))           # 1 = cudaStreamNonBlocking
    except Exception as e:
        print(f"overlap: no stream priorities ({e}); a plain non-blocking {what} stream", flush=True)
        return cp.cuda.Stream(non_blocking=True)


def sieve_stream(cp):
    """the sieve thread's non-blocking stream, by default of the highest priority (its CTAs are placed first when an SM slot frees: on an RTX PRO 6000 the sieve gets no SM time at all without it,
    for a Fermat CTA that does not leave room for a 10,240-register sieve CTA); OVERLAP_SIEVE_PRIORITY=0 gives it the default (lowest) priority, for a sieve CTA that fits in the registers the Fermat
    CTAs leave free (DEEP_TILE_MAXREG=32, 128-thread tile CTAs) with the Fermat streams above it (FERMAT_STREAM_PRIORITY=high); one per process"""
    if "s" not in _STREAM:
        _STREAM["s"] = new_stream(cp, int(os.environ.get("OVERLAP_SIEVE_PRIORITY", "-100")), "sieve")
    return _STREAM["s"]


def overlapped(cp, gen, depth=1):
    """iterate gen in a thread (device and stream set), hand its items over in order; depth items may wait in the queue"""
    dev = cp.cuda.Device().id
    q = queue.Queue(maxsize=depth)
    end = object()

    def work():
        try:
            cp.cuda.Device(dev).use()
            with sieve_stream(cp):
                for item in gen:
                    q.put(item)
            q.put(end)
        except BaseException as e:                                  # handed to the caller
            q.put(e)
    th = threading.Thread(target=work, daemon=True)
    th.start()
    while True:
        item = q.get()
        if item is end:
            break
        if isinstance(item, BaseException):
            raise item
        yield item
    th.join()


class Pipeline:
    """ONE sieve thread for the whole campaign: it plans the next batch itself and sieves its windows while the caller tests the pool of the previous window, across batch boundaries.

        pipe = Pipeline(cp, plan_next, make_windows)         # plan_next() -> the next batch (a list) or [] when nothing is left; both are called in the sieve thread only
        batch = pipe.next_batch()                            # [] = exhausted; the batch whose windows come next
        for item in pipe.windows(n):                         # exactly n items of make_windows(batch), in order (n = the number of windows of the batch)
            ...

    make_windows(batch) is a generator of (slice index, window) run in the sieve thread on the high-priority stream.  Memory bound: the thread starts a window only when fewer than `depth` windows
    are waiting for the caller (depth = 1: one window being sieved while the caller works on the one it took: two alive; depth = 2: up to two sieved ahead).  What the sieve hides under is the caller's
    flush (the Fermat rounds of its pool): with a flush per window (depth 1) the sieve of window i + 1 runs under the Fermat of window i; with ONE flush a batch (production's pool) the caller takes
    all the windows of batch n at once and flushes, and depth = the windows of a batch (2) lets the thread sieve the whole of batch n + 1 under that flush: no extra flush, no extra waste.
    Errors in the thread are re-raised in the caller at the next call.  take_stats() gives, since its last call, the seconds the caller waited for the thread (`wait`: sieve time NOT hidden), the
    seconds the thread spent making windows (`busy`) and waiting for the caller (`idle`: Fermat-bound), and the windows made.
    """
    def __init__(self, cp, plan_next, make_windows, depth=1):
        self.cp, self.plan_next, self.make_windows = cp, plan_next, make_windows
        self.q = queue.Queue()
        self.sem = threading.Semaphore(depth)
        self.th = None
        self.dev = cp.cuda.Device().id
        self.stats = dict(wait=0.0, busy=0.0, idle=0.0, windows=0)

    def take_stats(self):
        """the counters since the last call (seconds, windows), then reset; diagnostic (the two threads update different keys)"""
        st, self.stats = self.stats, dict(wait=0.0, busy=0.0, idle=0.0, windows=0)
        return st

    def _work(self):
        try:
            self.cp.cuda.Device(self.dev).use()
            with sieve_stream(self.cp):
                while True:
                    batch = self.plan_next()
                    self.q.put(("batch", batch))
                    if not batch:
                        return
                    gen = self.make_windows(batch)
                    while True:
                        t0 = time.perf_counter()
                        self.sem.acquire()                          # fewer than `depth` windows are waiting for the caller
                        t1 = time.perf_counter()
                        self.stats["idle"] += t1 - t0
                        try:
                            item = next(gen)
                        except StopIteration:
                            self.sem.release()
                            break
                        self.stats["busy"] += time.perf_counter() - t1
                        self.stats["windows"] += 1
                        self.q.put(("window", item))
        except BaseException as e:                                  # handed to the caller
            self.q.put(("error", e))

    def _get(self, want):
        if self.th is None:
            self.th = threading.Thread(target=self._work, daemon=True)
            self.th.start()
        t0 = time.perf_counter()
        kind, v = self.q.get()
        self.stats["wait"] += time.perf_counter() - t0
        if kind == "error":
            raise v
        assert kind == want, f"pipeline out of step: got {kind}, wanted {want}"
        return v

    def next_batch(self):
        return self._get("batch")

    def windows(self, n):
        for _ in range(n):
            item = self._get("window")
            self.sem.release()                                      # the sieve thread may start the next window
            yield item


class LruCache:
    """an OrderedDict with exact keys (no hashes: a collision would silently test the wrong numbers) and a size bound"""
    def __init__(self, size=512):
        self.size = size
        self.d = collections.OrderedDict()
        self.hits = self.misses = 0

    def get(self, key, make):
        v = self.d.get(key)
        if v is None:
            self.misses += 1
            v = self.d[key] = make()
            while len(self.d) > self.size:
                self.d.popitem(last=False)
        else:
            self.hits += 1
            self.d.move_to_end(key)
        return v

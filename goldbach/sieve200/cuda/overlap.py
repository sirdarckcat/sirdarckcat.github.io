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
import queue
import threading

_STREAM = {}


def sieve_stream(cp):
    """a non-blocking stream of the highest priority (a plain non-blocking stream if the priority calls are missing); one per process"""
    if "s" not in _STREAM:
        try:
            # 1 = cudaStreamNonBlocking; priority -100 is outside every device's range [-5 .. 0] and the driver clamps it to the greatest priority (cupy has no wrapper of
            # cudaDeviceGetStreamPriorityRange, only of cudaStreamCreateWithPriority)
            _STREAM["s"] = cp.cuda.ExternalStream(cp.cuda.runtime.streamCreateWithPriority(1, -100))
        except Exception as e:
            print(f"overlap: no stream priorities ({e}); a plain non-blocking stream", flush=True)
            _STREAM["s"] = cp.cuda.Stream(non_blocking=True)
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

    make_windows(batch) is a generator of (slice index, window) run in the sieve thread on the high-priority stream.  Memory bound: the thread starts a window only when the caller has taken the
    previous one (`depth` = 1: one window being sieved while one is consumed: two alive, not three).  A batch with fewer windows than the pool threshold still needs a flush per window to overlap anything:
    the Fermat rounds of window i are what the sieve of window i + 1 hides under.  Errors in the thread are re-raised in the caller at the next call.
    """
    def __init__(self, cp, plan_next, make_windows, depth=1):
        self.cp, self.plan_next, self.make_windows = cp, plan_next, make_windows
        self.q = queue.Queue()
        self.sem = threading.Semaphore(depth)
        self.th = None
        self.dev = cp.cuda.Device().id

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
                        self.sem.acquire()                          # the caller has taken the previous window
                        try:
                            item = next(gen)
                        except StopIteration:
                            self.sem.release()
                            break
                        self.q.put(("window", item))
        except BaseException as e:                                  # handed to the caller
            self.q.put(("error", e))

    def _get(self, want):
        if self.th is None:
            self.th = threading.Thread(target=self._work, daemon=True)
            self.th.start()
        kind, v = self.q.get()
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

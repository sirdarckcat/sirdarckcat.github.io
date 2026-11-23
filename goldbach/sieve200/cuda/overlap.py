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

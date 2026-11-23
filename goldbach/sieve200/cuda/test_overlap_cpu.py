#!/usr/bin/env python3
"""overlap.py without a GPU: order, run-ahead bound, error propagation, the exact-key cache (cupy replaced by a stub)."""
import os, sys, threading, time, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import overlap


def stub(priorities=True):
    cp = types.ModuleType("cupy")
    log = []
    class Stream:
        def __init__(self, *a, **k): log.append(("stream", threading.current_thread().name))
        def __enter__(self): log.append(("enter", threading.current_thread().name)); return self
        def __exit__(self, *a): log.append(("exit", threading.current_thread().name))
    class Dev:
        id = 0
        def __init__(self, i=0): self.i = i
        def use(self): log.append(("use", self.i))
    rt = types.SimpleNamespace()
    if priorities:
        rt.streamCreateWithPriority = lambda flags, prio: (flags, prio)
    cp.cuda = types.SimpleNamespace(Device=Dev, Stream=Stream, ExternalStream=lambda ptr: Stream(ptr), runtime=rt)
    return cp, log


def main():
    ok = True
    # 1. order and the thread / stream / device set up
    overlap._STREAM.clear()
    cp, log = stub()
    got = list(overlap.overlapped(cp, iter(range(50))))
    good = got == list(range(50)) and ("use", 0) in log and any(e[0] == "enter" and e[1] != threading.current_thread().name for e in log)
    print(f"  order of 50 items, device set and stream entered in the sieve thread: {'ok' if good else 'FAILED'}"); ok &= good
    # 2. the sieve runs ahead by at most the queue depth (+1 being made) while the consumer is slow
    overlap._STREAM.clear()
    cp, _ = stub()
    made = []
    def gen():
        for i in range(10):
            made.append(i)
            yield i
    it = overlap.overlapped(cp, gen(), depth=1)
    next(it)
    time.sleep(0.3)
    ahead = len(made) - 1                                          # items made beyond the one consumed
    good = 1 <= ahead <= 2
    print(f"  sieve ahead of a stalled consumer by {ahead} items (queue depth 1): {'ok' if good else 'FAILED'}"); ok &= good
    rest = list(it)
    good = rest == list(range(1, 10))
    print(f"  the rest arrives in order: {'ok' if good else 'FAILED'}"); ok &= good
    # 3. a slow consumer and a slow producer overlap (wall time ~ max, not the sum)
    overlap._STREAM.clear()
    cp, _ = stub()
    def slow_gen():
        for i in range(8):
            time.sleep(0.05); yield i
    t0 = time.time()
    for _ in overlap.overlapped(cp, slow_gen()):
        time.sleep(0.05)
    dt = time.time() - t0
    good = dt < 0.75 * (8 * 0.1)
    print(f"  8 items, 50 ms to make and 50 ms to consume: {dt:.2f} s against {8 * 0.1:.2f} s serial: {'ok' if good else 'FAILED'}"); ok &= good
    # 4. an error in the sieve thread is raised in the caller, after the items before it
    overlap._STREAM.clear()
    cp, _ = stub()
    def bad():
        yield 1; yield 2; raise RuntimeError("boom")
    seen = []
    try:
        for x in overlap.overlapped(cp, bad()):
            seen.append(x)
        good = False
    except RuntimeError as e:
        good = str(e) == "boom" and seen == [1, 2]
    print(f"  error in the sieve thread re-raised after items {seen}: {'ok' if good else 'FAILED'}"); ok &= good
    # 6. the cross-batch pipeline: batches planned in the thread, windows in order across batch boundaries, at most 2 windows alive, exhaustion, errors
    overlap._STREAM.clear()
    cp, _ = stub()
    plans = [["a", "b"], ["c"], ["d", "e", "f"]]
    alive, peak, produced, taken = [0], [0], [], []
    def plan_next():
        return plans.pop(0) if plans else []
    def make_windows(batch):
        for name in batch:
            for j in range(2):                                      # two windows a slice
                alive[0] += 1; peak[0] = max(peak[0], alive[0])
                produced.append((name, j))
                time.sleep(0.01)
                yield name, (name, j)
    pipe = overlap.Pipeline(cp, plan_next, make_windows)
    order = []
    while True:
        batch = pipe.next_batch()
        if not batch:
            break
        for si, w in pipe.windows(2 * len(batch)):
            order.append(w)
            time.sleep(0.03)                                        # a slow consumer: the thread runs ahead as far as the bound lets it
            alive[0] -= 1
    want = [(n, j) for b in (["a", "b"], ["c"], ["d", "e", "f"]) for n in b for j in range(2)]
    good = order == want and produced == want and peak[0] <= 2
    print(f"  pipeline over 3 batches (6 + 2 + 6 windows): order ok {order == want}, never more than 2 windows alive (peak {peak[0]}), exhaustion ends the loop: {'ok' if good else 'FAILED'}"); ok &= good
    # 6b. depth 2 with ONE flush a batch (production's pool): the consumer takes both windows of a batch, then "flushes" (sleeps); the thread must have sieved the whole next batch by then, never
    #     more than the held pool (2 windows) + depth (2) = 4 windows alive, and the counters add up
    overlap._STREAM.clear()
    cp, _ = stub()
    plans = [["a"], ["b"], ["c"]]
    alive, peak, produced = [0], [0], []
    def plan_next2():
        return plans.pop(0) if plans else []
    def make_windows2(batch):
        for name in batch:
            for j in range(2):
                alive[0] += 1; peak[0] = max(peak[0], alive[0])
                produced.append((name, j))
                time.sleep(0.02)
                yield name, (name, j)
    pipe = overlap.Pipeline(cp, plan_next2, make_windows2, depth=2)
    order, ahead = [], []
    while True:
        batch = pipe.next_batch()
        if not batch:
            break
        pool = [w for si, w in pipe.windows(2)]                     # the batch's pool: both windows taken at once
        order.extend(pool)
        alive[0] -= 0                                               # (the consumer keeps them until the flush is done)
        time.sleep(0.15)                                            # the flush: Fermat rounds
        ahead.append(len(produced))
        alive[0] -= 2
    st = pipe.take_stats()
    want = [("a", 0), ("a", 1), ("b", 0), ("b", 1), ("c", 0), ("c", 1)]
    good = order == want and peak[0] <= 4 and ahead == [4, 6, 6] and st["windows"] == 6 and st["busy"] > 0.1 and st["wait"] >= 0 and pipe.take_stats()["windows"] == 0
    print(f"  pipeline depth 2, one flush a batch: order ok {order == want}, windows made by the end of each flush {ahead} (4 = the next batch fully sieved under the flush), peak alive {peak[0]} <= 4 (the held pool of 2 + depth 2), "
          f"counters wait {st['wait']:.2f} busy {st['busy']:.2f} idle {st['idle']:.2f} s over {st['windows']} windows: {'ok' if good else 'FAILED'}"); ok &= good
    overlap._STREAM.clear()
    cp, _ = stub()
    def plan_bad():
        return ["x"]
    def mw_bad(batch):
        yield 0, "w0"
        raise RuntimeError("sieve broke")
    pipe = overlap.Pipeline(cp, plan_bad, mw_bad)
    try:
        pipe.next_batch()
        got = [w for _, w in pipe.windows(2)]
        good = False
    except RuntimeError as e:
        good = "sieve broke" in str(e)
    print(f"  pipeline error re-raised in the caller: {'ok' if good else 'FAILED'}"); ok &= good
    # 5. no priority calls: a plain non-blocking stream
    overlap._STREAM.clear()
    cp, log = stub(priorities=False)
    got = list(overlap.overlapped(cp, iter([7, 8])))
    good = got == [7, 8] and any(e[0] == "stream" for e in log)
    print(f"  without priority calls: {'ok' if good else 'FAILED'}"); ok &= good
    # 6. the cache: exact keys, hits, LRU eviction
    c = overlap.LruCache(size=3)
    made = []
    mk = lambda k: (lambda: made.append(k) or k)
    for k in ((1, (1, 2)), (2, (1, 2)), (1, (1, 2)), (1, (1, 3)), (3, (9,)), (4, (9,)), (1, (1, 2))):
        c.get(k, mk(k))
    good = c.hits == 1 and c.misses == 6 and len(c.d) == 3 and made.count((1, (1, 2))) == 2
    print(f"  cache: hits {c.hits} misses {c.misses} size {len(c.d)} (an evicted key is made again, a different row list is a different key): {'ok' if good else 'FAILED'}"); ok &= good
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""search_gpu5_poolsplitn.patch's run_pool_split (N = --pool-threads parts in N threads) on stubs: the function is taken from the patched driver (path in argv[1]) and run with a numpy-backed fake cupy and a
fake run_pool whose per-member results depend only on the member's own data.  For N = 1 .. 4 and several pool sizes the concatenated result must equal the unsplit run, every part gets the
target // N, the parts cover the pool exactly once, and an error in a thread is re-raised.

    python3 test_poolsplitn_fake.py /path/to/patched/search_gpu5.py
"""
import ast, sys, threading, types
import numpy as np

src = open(sys.argv[1]).read()
tree = ast.parse(src)
funcs = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef)}
assert {"run_pool_split", "_fermat_stream"} <= set(funcs), sorted(funcs)


class A(np.ndarray):
    """a numpy array with cupy's .get()"""
    def get(self):
        return np.asarray(self)


def wrap(x):
    return np.asarray(x).view(A)


class Stream:
    def __init__(self, non_blocking=False): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def synchronize(self): pass


class Dev:
    id = 0
    def __init__(self, i=0): pass
    def use(self): pass


cp = types.ModuleType("cupy")
cp.int64 = np.int64
cp.zeros = lambda n, dtype=None: wrap(np.zeros(n, dtype))
cp.cumsum = lambda x: wrap(np.cumsum(x))
cp.asarray = lambda x, dtype=None: wrap(np.asarray(x, dtype=dtype))
cp.concatenate = lambda xs: wrap(np.concatenate([np.asarray(x) for x in xs]))
cp.cuda = types.SimpleNamespace(Device=Dev, Stream=Stream, get_current_stream=lambda: Stream())
targets, lock = [], threading.Lock()
boom = [False]


def run_pool(tester, kv, cnt, cols, target=None):
    """per-member results that depend only on the member's own (kv, cnt, rows)"""
    if boom[0] and len(kv) and int(kv[0]) % 7 == 3:
        raise RuntimeError("boom")
    with lock:
        targets.append(target)
    kv, cnt, cols = np.asarray(kv), np.asarray(cnt), np.asarray(cols)
    ip = np.concatenate([[0], np.cumsum(cnt)])
    tests = cnt * 3 + kv % 5
    prp = (kv % 2 == 0)
    succ = (cnt == 0)
    frow = np.where(cnt > 0, cols[np.minimum(ip[:-1], max(len(cols) - 1, 0))] if len(cols) else -1, -1)
    return wrap(tests.astype(np.int64)), wrap(prp), wrap(succ), wrap(frow.astype(np.int64)), int(cnt.sum()), 7


ns = dict(cp=cp, np=np, threading=threading, os=__import__("os"), run_pool=run_pool, _SPLIT_STREAMS=[], args=types.SimpleNamespace(pool_threads=1, target=1 << 20))
exec(funcs["_fermat_stream"], ns)
exec(funcs["run_pool_split"], ns)
rng = np.random.default_rng(5)
ok = True
for N in (1, 2, 3, 4):
    ns["args"].pool_threads = N
    for n in (4096 * N + 17, 40_000, 100_003):
        cnt = rng.integers(0, 6, n).astype(np.int64)
        kv = rng.integers(0, 1 << 32, n).astype(np.int64)
        cols = (np.arange(int(cnt.sum())) * 7 + 3) % 1000
        targets.clear()
        out = ns["run_pool_split"](None, wrap(kv), wrap(cnt), wrap(cols))
        used = list(targets)                                    # (the reference run below adds its own target)
        ref = run_pool(None, kv, cnt, cols, target=1 << 20)
        same = all(np.array_equal(np.asarray(out[k]), np.asarray(ref[k])) for k in range(4)) and out[4] == ref[4]
        good = same and sorted(used) == [(1 << 20) // N] * N and out[5] == 7 * N and len(ns["_SPLIT_STREAMS"]) >= N
        print(f"  N={N} n={n}: concatenated result identical to the unsplit run, {len(used)} parts with target {(1 << 20) // N}: {'ok' if good else 'FAILED'}")
        ok &= good
# a pool too small to split goes to run_pool as it is
ns["args"].pool_threads = 3
targets.clear()
out = ns["run_pool_split"](None, wrap(np.arange(100)), wrap(np.ones(100, np.int64)), wrap(np.arange(100)))
good = targets == [None] and len(out[0]) == 100
print(f"  a pool of 100 members is not split: {'ok' if good else 'FAILED'}")
ok &= good
# an error in a part is re-raised
boom[0] = True
ns["args"].pool_threads = 4
try:
    kv = np.arange(40_000, dtype=np.int64) * 7 + 3
    ns["run_pool_split"](None, wrap(kv), wrap(np.ones(40_000, np.int64)), wrap(np.arange(40_000)))
    good = False
except RuntimeError as e:
    good = str(e) == "boom"
print(f"  an error in a thread is re-raised: {'ok' if good else 'FAILED'}")
ok &= good
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)

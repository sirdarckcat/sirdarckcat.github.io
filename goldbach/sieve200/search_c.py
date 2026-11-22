#!/usr/bin/env python3
"""search_c.py -- search.py with the sieve of run_block in C (sieve200).  Same command line, same log lines, same results.

    python3 goldbach/sieve200/search_c.py slice.json --procs 4 --sort-tests --skip-frac 0.92 --p-est 0.055 \
            --sieve-b 1000000 --out found.jsonl

It imports goldbach/search.py and replaces two of its functions, init_spec and run_block (see search.run_block for the
semantics, which are kept exactly: the alive matrix, the counts, the order in which members are tested, the Fermat loop
that stops at a member's first probable prime, and the six returned numbers).  search.search_spec, the log line, the
verification and the output file are search.py's own, untouched.

The sieve runs on a window of K = 2^logK members (default: the smallest power of two >= 4 blocks, so 2^17 for the
default block of 32768); a worker sieves the window starting at the first block it is asked for and serves the next
blocks from it.  Pool.imap is given chunksize = K / block so that a worker is asked for consecutive blocks; with fewer than
`procs` chunks the pool would idle, so the chunk is lowered until there are at least `procs` of them.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np  # noqa: E402
import search  # noqa: E402
from search import G, mpz, powmod  # noqa: E402
import sieve200  # noqa: E402
from sieve200 import Sieve200  # noqa: E402

try:
    sieve200.load()                                               # compiles the C file on first use (needs gcc)
    HAVE_C = True
except Exception as e:                                          # no compiler, odd platform: search.py's own sieve
    print(f"search_c.py: cannot build sieve200 ({e}); using search.py's numpy sieve", file=sys.stderr, flush=True)
    HAVE_C = False

CHUNK_BLOCKS = int(os.environ.get("SEARCH_C_CHUNK", "4"))     # blocks a worker sieves at a time (a power of two)
MEMBER_GROUP = 2048                                           # members whose row lists are extracted at once


def init_spec(spec, sieve_b, block):
    N0 = mpz(spec["N0"])
    M = mpz(spec["M"])
    U = [int(q) for q in spec["residual"]]
    cover = [int(r) for r, _ in spec.get("cover", [])]
    chunk = max(1, CHUNK_BLOCKS)
    logK = max(9, math.ceil(math.log2(block * chunk))) if block * chunk > 1 else 9
    sv = Sieve200(int(N0), int(M), U, sieve_b, logK=logK, exclude=cover)
    G.clear()
    G.update(N0=N0, M=M, U=U, block=block, Q=spec["Q"], cq=[N0 - q for q in U], sv=sv, cache=None,
             chunk=max(1, sv.K // block))


def _window(k0):
    """counts (u16, K) and bit rows of a window of members containing the whole block k0 .. k0 + L - 1."""
    sv, L = G["sv"], G["block"]
    c = G["cache"]
    if c is None or not (c[0] <= k0 and k0 + L <= c[0] + sv.K):
        cnt, bits = sv.block(k0)
        c = G["cache"] = (k0, cnt, bits)
    return c


def run_block(k0):
    """Scan [k0, k0+block).  Returns (successes, tests, prps, alive_total, hm_kept, hm_all), as search.run_block."""
    M, L, cq = G["M"], G["block"], G["cq"]
    sv = G["sv"]
    kb, cnt_all, bits = _window(k0)
    off = k0 - kb
    counts = cnt_all[off:off + L].astype(np.int64)                  # the reference's aliveT.sum(axis=1)
    alive_total = int(counts.sum())
    tests = prps = 0
    successes = []
    order = np.argsort(counts, kind="stable") if G.get("sort_tests") else range(L)
    skip = G.get("skip_frac", 0.0)
    hm_kept = hm_all = 1.0
    if skip > 0.0:
        p = G.get("p_est", 0.06)
        w = (1.0 - p) ** counts.astype(np.float64)
        keep = int(math.ceil(L * (1.0 - skip)))
        order = np.argsort(counts, kind="stable")[:keep]
        hm_kept = float(w[order].sum())
        hm_all = float(w.sum())
    order = np.asarray(order, dtype=np.int64)
    for g in range(0, len(order), MEMBER_GROUP):
        js = np.ascontiguousarray(order[g:g + MEMBER_GROUP] + off, dtype=np.uint32)
        rows, offs = sv.survivors(bits, js)
        rows = rows.tolist()
        offs = offs.tolist()
        for t in range(len(js)):
            j = int(order[g + t])
            a, b = offs[t], offs[t + 1]
            if a == b:
                successes.append(k0 + j)                           # fully sieved out -> success
                continue
            kM = (k0 + j) * M
            ok = True
            for i in rows[a:b]:
                n = cq[i] + kM
                tests += 1
                if powmod(2, n - 1, n) == 1:
                    prps += 1
                    ok = False
                    break
            if ok:
                successes.append(k0 + j)
    return successes, tests, prps, alive_total, hm_kept, hm_all


class _Pool:
    """multiprocessing.Pool whose imap hands a worker `chunk` consecutive blocks (so that one sieve window serves them)."""

    def __init__(self, procs):
        import multiprocessing.pool
        self._pool = multiprocessing.pool.Pool(procs)
        self._procs = procs

    def __enter__(self):
        self._pool.__enter__()
        return self

    def __exit__(self, *a):
        return self._pool.__exit__(*a)

    def imap(self, func, iterable, chunksize=1):
        items = list(iterable)
        chunk = G.get("chunk", 1)
        while chunk > 1 and len(items) < self._procs * chunk:
            chunk //= 2
        return self._pool.imap(func, items, chunksize=chunk)

    def terminate(self):
        self._pool.terminate()

    def __getattr__(self, name):
        return getattr(self._pool, name)


if HAVE_C:
    search.init_spec = init_spec
    search.run_block = run_block
    search.Pool = _Pool

if __name__ == "__main__":
    search.main()

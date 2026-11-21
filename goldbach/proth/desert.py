"""Proth/BLS-certified Goldbach deserts: build + search.

Idea (see README.md).  Every record in this repo so far proves the Goldbach
partition N = g + (N - g) with an ECPP certificate for the complement
N - g, and ECPP is what caps the height game ("Game 1") near 3-4k digits.
Here the complement is *constructed* in the form

        P = N - g = m * 2^n + 1,        2^(3n) > P,

so that its primality follows from one modular exponentiation
(Pocklington / Brillhart-Lehmer-Selfridge N-1 test with the fully factored
part F = 2^n > P^(1/3)).  The covering congruences N = a_r (mod r) become
congruences on m (2^n is invertible mod every odd r), so nothing is lost:

        m = (a_r - g - 1) * 2^(-n)   (mod r)   for every cover prime r.

With certification free, a *full* cover (every prime q < g killed by a
congruence divisor, no residual lottery at all) is the cheapest design, and
the whole proof of g(N) = g is: a sieve check of the cover plus one modexp.

Usage:
    desert.py build  Q out.json [--proth] [--increasing]   # cover, g, n, m0, Mc
    desert.py search spec.json out_dir [--procs 4] [--sieve 1e9] [--T 16384]
"""
import json
import math
import os
import sys
import time

import numpy as np
import gmpy2
from gmpy2 import mpz


# ----------------------------------------------------------------- primes --
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


def is_small_prime(q):
    if q < 2:
        return False
    i = 2
    while i * i <= q:
        if q % i == 0:
            return False
        i += 1
    return True


# ------------------------------------------------------------------ cover --
def increasing_full_cover(Q):
    """The paper's algorithm: one residue class per odd prime r = 3, 5, 7, ...
    in increasing order, each taking the class holding the most still-uncovered
    odd primes < Q (smallest residue on ties), until none is left."""
    rmax_guess = max(1000, int(2.2 * Q ** 0.72))
    while True:
        P = primes_upto(max(Q, rmax_guess))
        alive = P[(P >= 3) & (P < Q)].astype(np.int64)
        cover = []
        for r in P[(P >= 3) & (P <= rmax_guess)]:
            r = int(r)
            if len(alive) == 0:
                break
            res = alive % r
            cnt = np.bincount(res, minlength=r)
            a = int(cnt.argmax())
            alive = alive[res != a]
            cover.append((r, a))
        if len(alive) == 0:
            return cover
        rmax_guess *= 2


def lazy_full_cover(Q, pool_factor=3.0):
    """Weighted set-cover greedy over ALL odd primes r <= pool: repeatedly take
    the (r, class) maximising  kills / ln r  against the current survivors.
    Gains only shrink as survivors are removed, so lazy re-evaluation from a
    heap is exact.  Each modulus is used while its best class is still intact,
    which removes most of the one-kill tail of the fixed-order greedy
    (about 10% fewer digits).  Deterministic."""
    import heapq
    pool = int(pool_factor * max(r for r, _ in increasing_full_cover(Q)))
    P = primes_upto(max(Q, pool))
    alive = P[(P >= 3) & (P < Q)].astype(np.int64)
    heap = []
    for r in P[(P >= 3) & (P <= pool)]:
        r = int(r)
        cnt = np.bincount(alive % r, minlength=r)
        a = int(cnt.argmax())
        heap.append((-int(cnt[a]) / math.log(r), r, a, 0))
    heapq.heapify(heap)
    cover, stamp = [], 0
    while len(alive):
        _, r, a, st = heapq.heappop(heap)
        res = alive % r
        if st != stamp:
            cnt = np.bincount(res, minlength=r)
            a = int(cnt.argmax())
            if cnt[a] == 0:
                continue
            sc = -int(cnt[a]) / math.log(r)
            if heap and sc > heap[0][0]:
                heapq.heappush(heap, (sc, r, a, stamp))
                continue
        alive = alive[res != a]
        cover.append((r, a))
        stamp += 1
    return sorted(cover)


def greedy_full_cover(Q, order="lazy", verbose=True):
    cover = lazy_full_cover(Q) if order == "lazy" else increasing_full_cover(Q)
    if verbose:
        logm = sum(math.log(r) for r, _ in cover)
        print(f"full cover of odd primes < {Q} ({order}): {len(cover)} odd moduli, "
              f"r_max = {cover[-1][0]}, prod r = {logm / math.log(10):.1f} digits")
    return cover


def covered_mask(limit, cover):
    """mask[x] = True iff x = a_r (mod r) for some cover class."""
    mask = np.zeros(limit, dtype=bool)
    for r, a in cover:
        mask[a::r] = True
    return mask


def least_uncovered_prime(Q, cover):
    """Least prime g >= Q in no cover class.  Every prime in [Q, g) is then
    covered too, so the cover kills *every* prime below g."""
    span = 1 << 16
    while True:
        mask = covered_mask(Q + span, cover)
        P = primes_upto(Q + span)
        P = P[P >= Q]
        unc = P[~mask[P]]
        if len(unc):
            return int(unc[0])
        span *= 2


# -------------------------------------------------------------------- CRT --
def build_spec(Q, proth=False, tbits=20, order="lazy"):
    cover = greedy_full_cover(Q, order)
    g = least_uncovered_prime(Q, cover)
    Mc = mpz(1)
    for r, _ in cover:
        Mc *= r
    bm = int(Mc.bit_length()) + tbits          # m = m0 + t*Mc < 2^bm
    # P < 2^(n+bm) + 1.  BLS needs 2^(3n) > P; Proth/Pocklington 2^(2n) > P.
    n = bm + 1 if proth else (bm + 2) // 2 + 1
    m0, M = mpz(0), mpz(1)
    for r, a in cover:
        c = ((a - g - 1) * pow(pow(2, n, r), -1, r)) % r
        t = ((c - int(m0 % r)) * pow(int(M % r), -1, r)) % r
        m0 += M * t
        M *= r
    assert M == Mc
    # fixed witness base: a cover prime b that is a non-residue of P.  P mod b
    # is the same for every candidate (b | Mc), and P = 1 (mod 4), so
    # (b/P) = (P/b) = ((a_b - g)/b).
    base = None
    for r, a in cover:
        if gmpy2.jacobi((a - g) % r, r) == -1:
            base = r
            break
    spec = {
        "Q": Q, "g": g, "n": n, "mode": "proth" if proth else "bls",
        "tbits": tbits, "base": base, "cover_order": order,
        "cover": [[2, 0]] + [[r, a] for r, a in cover],
        "Mc": str(Mc), "m0": str(m0),
        "Mc_digits": len(str(Mc)),
        "P_bits_est": n + bm,
    }
    print(f"g = {g}  n = {n}  base = {base}  "
          f"P ~ {n + bm} bits ~ {int((n + bm) * 0.30103)} digits")
    return spec


# ------------------------------------------------------------------ sieve --
def _sieve_chunk(args):
    lo, hi, n, m0s, Mcs, T, cover_mods = args
    m0, Mc = mpz(m0s), mpz(Mcs)
    # segmented sieve of [lo, hi)
    root = int(hi ** 0.5) + 1
    small = primes_upto(root)
    seg = np.ones(hi - lo, dtype=bool)
    for p in small:
        p = int(p)
        start = max(p * p, ((lo + p - 1) // p) * p)
        seg[start - lo::p] = False
    ps = (np.nonzero(seg)[0] + lo).astype(np.uint64)
    ps = ps[(ps > 2) & ~np.isin(ps, cover_mods)]
    if len(ps) == 0:
        return np.zeros(0, dtype=np.int64)
    plist = ps.tolist()
    rm0 = np.array([int(m0 % s) for s in plist], dtype=np.uint64)
    rMc = np.array([int(Mc % s) for s in plist], dtype=np.uint64)
    # 2^n mod s
    two = np.ones(len(ps), dtype=np.uint64)
    for bit in bin(n)[2:]:
        two = (two * two) % ps
        if bit == "1":
            two = (two * np.uint64(2)) % ps
    # t0 = (-1 - 2^n m0) * (2^n Mc)^-1 mod s
    num = (ps - np.uint64(1) + ps - (two * rm0) % ps) % ps
    den = (two * rMc) % ps
    # inverse by Fermat, vectorised
    inv = np.ones(len(ps), dtype=np.uint64)
    e = ps - np.uint64(2)
    b = den.copy()
    for _ in range(31):
        odd = (e & np.uint64(1)).astype(bool)
        inv[odd] = (inv[odd] * b[odd]) % ps[odd]
        b = (b * b) % ps
        e >>= np.uint64(1)
    t0 = (num * inv) % ps
    assert (den != 0).all()
    out = [t0[t0 < np.uint64(T)].astype(np.int64)]
    for s_, t_ in zip(ps[ps < np.uint64(T)].tolist(), t0[ps < np.uint64(T)].tolist()):
        out.append(np.arange(t_, T, s_, dtype=np.int64))      # all t = t0 (mod s)
    return np.concatenate(out)


def sieve_candidates(spec, T, B, procs):
    from multiprocessing import Pool
    cover_mods = np.array([r for r, _ in spec["cover"]], dtype=np.uint64)
    step = 4_000_000
    jobs = [(lo, min(lo + step, B), spec["n"], spec["m0"], spec["Mc"], T, cover_mods)
            for lo in range(2, B, step)]
    alive = np.ones(T, dtype=bool)
    t0 = time.time()
    with Pool(procs) as pool:
        for i, hit in enumerate(pool.imap_unordered(_sieve_chunk, jobs, chunksize=4)):
            alive[hit] = False
            if i % 50 == 0:
                print(f"  sieve {i}/{len(jobs)} chunks, alive {int(alive.sum())}/{T}, "
                      f"{time.time() - t0:.0f}s", flush=True)
    return np.nonzero(alive)[0]


# ------------------------------------------------------------------- test --
_G = {}


def _init_test(n, m0s, Mcs, base):
    _G.update(n=n, m0=mpz(m0s), Mc=mpz(Mcs), base=base)


def _test(t):
    t0 = time.time()
    m = _G["m0"] + t * _G["Mc"]
    P = (m << _G["n"]) + 1
    x = gmpy2.powmod(_G["base"], (P - 1) >> 1, P)
    return t, bool(x == P - 1), time.time() - t0


def bls_prove(P, base):
    """Return a description string if P is PROVEN prime by the N-1 test with
    F = 2^v (v = v2(P-1)); raise if the proof does not go through."""
    P = mpz(P)
    v = gmpy2.bit_scan1(P - 1)
    F = mpz(1) << v
    assert gmpy2.powmod(base, (P - 1) >> 1, P) == P - 1, "Euler condition fails"
    # => every prime factor of P is = 1 (mod F)
    if F * F > P:
        return f"Pocklington (F = 2^{v} > sqrt(P))"
    assert F ** 3 > P, "factored part too small"
    q = (P - 1) >> v
    c1, c2 = q % F, q >> v
    D = c1 * c1 - 4 * c2
    assert D < 0 or gmpy2.isqrt(D) ** 2 != D, "c1^2 - 4 c2 is a square: composite"
    return f"BLS (F = 2^{v} > P^(1/3), c1^2 - 4 c2 not a square)"


def search(spec, out_dir, procs=4, B=10 ** 9, T=16384):
    from multiprocessing import Pool
    os.makedirs(out_dir, exist_ok=True)
    assert T < (1 << spec["tbits"])
    surv_path = f"{out_dir}/survivors_T{T}_B{B}.json"
    if os.path.exists(surv_path):
        surv = json.load(open(surv_path))
    else:
        surv = [int(t) for t in sieve_candidates(spec, T, B, procs)]
        json.dump(surv, open(surv_path, "w"))
    log_path = f"{out_dir}/tests.jsonl"
    done = {}
    if os.path.exists(log_path):
        for line in open(log_path):
            d = json.loads(line)
            done[d["t"]] = d["ok"]
    hits = [t for t, ok in done.items() if ok]
    todo = [t for t in surv if t not in done]
    lnP = spec["P_bits_est"] * math.log(2)
    print(f"{len(surv)} sieve survivors of {T}; {len(done)} already tested; "
          f"expected tests per prime ~ {lnP / (1.781 * math.log(B)):.0f}", flush=True)
    t_start = time.time()
    if not hits:
        with Pool(procs, initializer=_init_test,
                  initargs=(spec["n"], spec["m0"], spec["Mc"], spec["base"])) as pool, \
                open(log_path, "a") as log:
            for i, (t, ok, dt) in enumerate(pool.imap_unordered(_test, todo, chunksize=1)):
                log.write(json.dumps({"t": t, "ok": ok, "sec": round(dt, 2)}) + "\n")
                log.flush()
                if i % 20 == 0 or ok:
                    print(f"  test {len(done) + i + 1}: t={t} ok={ok} {dt:.1f}s "
                          f"elapsed {time.time() - t_start:.0f}s", flush=True)
                if ok:
                    hits.append(t)
                    pool.terminate()
                    break
    if not hits:
        print("no prime in this window; rerun with a larger --T")
        return None
    t = min(hits)
    m = mpz(spec["m0"]) + t * mpz(spec["Mc"])
    P = (m << spec["n"]) + 1
    how = bls_prove(P, spec["base"])
    N = P + spec["g"]
    rec = {
        "game": "height (Game 1), Proth/BLS-certified full cover",
        "g": spec["g"], "Q": spec["Q"], "digits": len(str(N)),
        "n": spec["n"], "t": t, "base": spec["base"], "proof": how,
        "cover": spec["cover"],
        "m": str(m), "N": str(N),
        "tests_run": len(done) + (len(todo) and 0) ,
    }
    rec["tests_run"] = sum(1 for _ in open(log_path))
    json.dump(rec, open(f"{out_dir}/record.json", "w"))
    print(f"HIT t={t}: N has {rec['digits']} digits, g(N) = {spec['g']}; {how}")
    return rec


def main():
    cmd = sys.argv[1]
    if cmd == "build":
        Q, out = int(float(sys.argv[2])), sys.argv[3]
        spec = build_spec(Q, proth="--proth" in sys.argv,
                          order="increasing" if "--increasing" in sys.argv else "lazy")
        json.dump(spec, open(out, "w"))
        print("wrote", out)
    elif cmd == "search":
        spec = json.load(open(sys.argv[2]))
        out_dir = sys.argv[3]
        opt = dict(zip(sys.argv[4::2], sys.argv[5::2]))
        search(spec, out_dir, procs=int(opt.get("--procs", 4)),
               B=int(float(opt.get("--sieve", 1e9))), T=int(opt.get("--T", 16384)))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

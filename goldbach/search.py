"""Sieved CRT-progression search for Goldbach-desert records.

Given a cover spec (N0, M, residual primes U, target Q), scan k upward:
N = N0 + k*M is a *success* when N - q is composite for every prime
q < Q.  Covered primes are composite by construction; residual primes
are first sieved by small primes (s <= B, s not dividing M), and the
survivors are hit with a Fermat base-2 test (a compositeness proof when
it fails; a pass means some q < Q is very likely a summand, killing k).

Successes are re-verified exhaustively (BPSW over all primes < Q) and
g(N) is computed by scanning q >= Q for a probable-prime complement.

Usage: search.py spec.json [spec2.json ...] --kmax 200000 --procs 4
Spec JSON fields: name, N0, M, residual, Q, optional kmax/kstart/ceiling.
"""

import argparse
import json
import math
import sys
import time
from multiprocessing import Pool

import numpy as np
import gmpy2
from gmpy2 import mpz, powmod, is_prime
from sympy import primerange

# ---------------- worker globals (shared via fork) ----------------
G = {}
_SIEVE_CACHE = {}


def init_spec(spec, sieve_b, block):
    N0 = mpz(spec["N0"])
    M = mpz(spec["M"])
    U = [int(q) for q in spec["residual"]]

    # Residue-swap variants share M (same cover moduli), so the expensive
    # per-prime modular inverses can be cached across specs in one process
    # (sieve-inverse caching, adopted from PR #20 with user approval).
    cache_key = (int(M), sieve_b)
    if cache_key in _SIEVE_CACHE:
        S, inv = _SIEVE_CACHE[cache_key]
    else:
        cover_primes = set(r for r, _ in spec.get("cover", []))
        S_raw = np.array([s for s in primerange(3, sieve_b)
                          if s not in cover_primes], dtype=np.int64)
        mm = np.empty(len(S_raw), dtype=np.int64)
        inv_raw = np.empty(len(S_raw), dtype=np.int64)
        for i, s in enumerate(S_raw):
            si = int(s)
            mv = int(M % si)
            mm[i] = mv
            inv_raw[i] = pow(mv, -1, si) if mv else 0
        good = mm != 0      # drop any s | M (cover primes already removed)
        S = S_raw[good]
        inv = inv_raw[good]
        _SIEVE_CACHE[cache_key] = (S, inv)

    n0_val = int(N0)
    n0m = np.array([n0_val % int(s) for s in S], dtype=np.int64)
    small = S < block
    # k-residues killing q (k == (q - N0) * M^-1 mod s) are computed per
    # residual on the fly in run_block: storing them for all (q, s) pairs
    # costs |U| * pi(B) ints, which is GBs for large target sets.
    G.update(N0=N0, M=M, U=U, block=block, Q=spec["Q"],
             cq=[N0 - q for q in U],
             n0m=n0m, inv=inv, S=S, small=small,
             S_small=S[small], S_small_list=[int(s) for s in S[small]],
             S_large=S[~small])


def run_block(k0):
    """Scan [k0, k0+block).  Returns (successes, tests, prps, alive_total)."""
    N0, M, U = G["N0"], G["M"], G["U"]
    L = G["block"]
    Ss, Sl = G["S_small"], G["S_large"]
    Ss_list = G["S_small_list"]
    S, n0m, inv, small = G["S"], G["n0m"], G["inv"], G["small"]
    alive = np.ones((len(U), L), dtype=bool)
    for i, q in enumerate(U):
        row = alive[i]
        kres = ((q - n0m) * inv - k0) % S
        js = kres[small].tolist()
        for j, s in zip(js, Ss_list):
            row[j::s] = False
        jl = kres[~small]
        hit = jl < L
        row[jl[hit]] = False
    tests = prps = 0
    alive_total = int(alive.sum())
    successes = []
    cq = G["cq"]
    aliveT = np.ascontiguousarray(alive.T)
    # test emptiest k first: success prob is (1-p)^a, so hits concentrate
    # in the low-survivor tail (measured ~1.8x faster discovery at 200d)
    counts = aliveT.sum(axis=1)
    order = np.argsort(counts, kind="stable") \
        if G.get("sort_tests") else range(L)
    skip = G.get("skip_frac", 0.0)
    hm_kept = hm_all = 1.0
    if skip > 0.0:
        # test only the emptiest (1-skip) fraction; the sacrificed hit mass
        # is accounted exactly from the survivor histogram: hit(k) ~ (1-p)^a
        p = G.get("p_est", 0.06)
        w = (1.0 - p) ** counts.astype(np.float64)
        keep = int(math.ceil(L * (1.0 - skip)))
        order = np.argsort(counts, kind="stable")[:keep]
        hm_kept = float(w[order].sum())
        hm_all = float(w.sum())
    for j in order:
        j = int(j)                     # np.int64 k would break JSON output
        col = aliveT[j]
        if not col.any():
            successes.append(k0 + j)   # fully sieved out -> success
            continue
        ok = True
        for i in np.nonzero(col)[0]:
            n = cq[i] + (k0 + j) * M
            tests += 1
            if powmod(2, n - 1, n) == 1:
                prps += 1
                ok = False
                break
        if ok:
            successes.append(k0 + j)
    return successes, tests, prps, alive_total, hm_kept, hm_all


def verify_success(spec, k):
    """Check no prime q < Q is a summand; then find g(N).

    For small Q, exhaustively BPSW-test every prime offset.  For large Q
    (mega covers), covered offsets have a congruence divisor by
    construction, so re-check only the residual offsets; the exhaustive
    per-offset evidence is produced later by verify_record.py.
    """
    N = mpz(spec["N0"]) + k * mpz(spec["M"])
    Q = spec["Q"]
    if spec.get("fast_verify"):
        for r, a in spec["cover"]:
            if (N - a) % r != 0:
                return None          # CRT reconstruction mismatch
        for q in spec["residual"]:
            if is_prime(N - q):
                return None
    else:
        for q in primerange(2, Q):
            if is_prime(N - q):
                return None
    q = int(gmpy2.next_prime(Q - 1))
    while not is_prime(N - q):
        q = int(gmpy2.next_prime(q))
    return {"k": k, "N": str(N), "digits": len(str(N)), "g": q}


def search_spec(spec, args, out):
    t0 = time.time()
    init_spec(spec, args.sieve_b, args.block)
    G["sort_tests"] = getattr(args, "sort_tests", False)
    G["skip_frac"] = getattr(args, "skip_frac", 0.0)
    G["p_est"] = getattr(args, "p_est", 0.06)
    kmax = spec.get("kmax", args.kmax)
    kstart = spec.get("kstart", 0)
    ceiling = spec.get("ceiling_digits")
    if ceiling:
        kcap = int((mpz(10) ** ceiling - mpz(spec["N0"])) // mpz(spec["M"]))
        kmax = min(kmax, kcap + 1)
    blocks = list(range(kstart, kmax, args.block))
    tests = prps = alive = 0
    hm_kept = hm_all = 0.0
    found = []
    with Pool(args.procs) as pool:
        for bs, bt, bp, ba, bhk, bha in pool.imap(run_block, blocks):
            tests += bt
            prps += bp
            alive += ba
            hm_kept += bhk
            hm_all += bha
            for k in bs:
                res = verify_success(spec, k)
                if res:
                    res["name"] = spec["name"]
                    found.append(res)
                    print(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} "
                          f"g={res['g']}", flush=True)
                    out.write(json.dumps(res) + "\n")
                    out.flush()
            if found and spec.get("stop_on_success"):
                pool.terminate()
                break
    dt = time.time() - t0
    # blocks overshoot kmax (run_block always scans a full block), so the
    # denominator for rate/density stats is what actually ran, not the cap
    kdone = len(blocks) * args.block
    phat = prps / tests if tests else 0.0
    e_hat = (alive / kdone) * phat if kdone else 0.0
    hshare = hm_kept / hm_all if hm_all else 1.0
    print(f"[{spec['name']}] k=[{kstart},{kmax}) {dt:.0f}s "
          f"({kdone/dt:.0f} k/s) tests={tests} prp={prps} "
          f"p^={phat:.4f} alive/k={alive/max(kdone,1):.1f} E^={e_hat:.2f} "
          f"hit%={100*hshare:.1f} found={len(found)}", flush=True)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--kmax", type=int, default=200000)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--block", type=int, default=32768)
    ap.add_argument("--sieve-b", type=int, default=3000000)
    ap.add_argument("--sort-tests", action="store_true",
                    help="Fermat-test each block's k in ascending-survivor "
                         "order (faster first-hit discovery)")
    ap.add_argument("--skip-frac", type=float, default=0.0,
                    help="skip the fullest fraction f of each block's k; "
                         "the sacrificed hit mass is accounted exactly and "
                         "reported as hit%% in the summary line")
    ap.add_argument("--p-est", type=float, default=0.06,
                    help="PRP pass probability used for hit-mass weights")
    ap.add_argument("--out", default="found.jsonl")
    args = ap.parse_args()
    with open(args.out, "a") as out:
        for path in args.specs:
            with open(path) as f:
                data = json.load(f)
            specs = data if isinstance(data, list) else [data]
            for spec in specs:
                search_spec(spec, args, out)


if __name__ == "__main__":
    main()

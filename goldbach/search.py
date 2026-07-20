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


def init_spec(spec, sieve_b, block):
    N0 = mpz(spec["N0"])
    M = mpz(spec["M"])
    U = [int(q) for q in spec["residual"]]
    cover_primes = set(r for r, _ in spec.get("cover", []))
    S = np.array([s for s in primerange(3, sieve_b) if s not in cover_primes],
                 dtype=np.int64)
    n0m = np.empty(len(S), dtype=np.int64)
    mm = np.empty(len(S), dtype=np.int64)
    inv = np.empty(len(S), dtype=np.int64)
    for i, s in enumerate(S):
        si = int(s)
        n0m[i] = int(N0 % si)
        mv = int(M % si)
        mm[i] = mv
        inv[i] = pow(mv, -1, si) if mv else 0
    good = mm != 0          # drop any s | M (cover primes already removed)
    S, n0m, inv = S[good], n0m[good], inv[good]
    # k-residues killing q: k == (q - N0) * M^-1  (mod s)
    kres = {}
    for q in U:
        kres[q] = ((q - n0m) * inv) % S
    small = S < block
    G.update(N0=N0, M=M, U=U, block=block, Q=spec["Q"],
             cq=[N0 - q for q in U],
             S_small=S[small], S_small_list=[int(s) for s in S[small]],
             S_large=S[~small],
             kres_small={q: kres[q][small] for q in U},
             kres_large={q: kres[q][~small] for q in U})


def run_block(k0):
    """Scan [k0, k0+block).  Returns (successes, tests, prps, alive_total)."""
    N0, M, U = G["N0"], G["M"], G["U"]
    L = G["block"]
    Ss, Sl = G["S_small"], G["S_large"]
    Ss_list = G["S_small_list"]
    alive = np.ones((len(U), L), dtype=bool)
    for i, q in enumerate(U):
        row = alive[i]
        js = ((G["kres_small"][q] - k0) % Ss).tolist()
        for j, s in zip(js, Ss_list):
            row[j::s] = False
        jl = (G["kres_large"][q] - k0) % Sl
        hit = jl < L
        row[jl[hit]] = False
    tests = prps = 0
    alive_total = int(alive.sum())
    successes = []
    cq = G["cq"]
    for j in range(L):
        col = alive[:, j]
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
    return successes, tests, prps, alive_total


def verify_success(spec, k):
    """Exhaustive check: no prime q < Q is a summand; then find g(N)."""
    N = mpz(spec["N0"]) + k * mpz(spec["M"])
    Q = spec["Q"]
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
    kmax = spec.get("kmax", args.kmax)
    kstart = spec.get("kstart", 0)
    ceiling = spec.get("ceiling_digits")
    if ceiling:
        kcap = int((mpz(10) ** ceiling - mpz(spec["N0"])) // mpz(spec["M"]))
        kmax = min(kmax, kcap + 1)
    blocks = list(range(kstart, kmax, args.block))
    tests = prps = alive = 0
    found = []
    with Pool(args.procs) as pool:
        for bs, bt, bp, ba in pool.imap(run_block, blocks):
            tests += bt
            prps += bp
            alive += ba
            for k in bs:
                res = verify_success(spec, k)
                if res:
                    res["name"] = spec["name"]
                    found.append(res)
                    print(f"  SUCCESS {spec['name']} k={k} digits={res['digits']} "
                          f"g={res['g']}", flush=True)
                    out.write(json.dumps(res) + "\n")
                    out.flush()
    dt = time.time() - t0
    kdone = kmax - kstart
    phat = prps / tests if tests else 0.0
    e_hat = (alive / kdone) * phat if kdone else 0.0
    print(f"[{spec['name']}] k=[{kstart},{kmax}) {dt:.0f}s "
          f"({kdone/dt:.0f} k/s) tests={tests} prp={prps} "
          f"p^={phat:.4f} alive/k={alive/max(kdone,1):.1f} E^={e_hat:.2f} "
          f"found={len(found)}", flush=True)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--kmax", type=int, default=200000)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--block", type=int, default=16384)
    ap.add_argument("--sieve-b", type=int, default=3000000)
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

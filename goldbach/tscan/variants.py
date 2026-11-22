#!/usr/bin/env python3
"""All near-optimal residue vectors on a cover's primes, as scan specs.

    python3 variants.py base_spec.json D out.json

base_spec.json is a cover.py output: congruences N = a_r (mod r) for a set
of small primes r, and the residual primes q < Q that no congruence covers.
cover.py picks the residues greedily.  This script keeps the primes r and
enumerates EVERY choice of nonzero residues whose residual set has at most
D primes more than the greedy one (depth-first, pruned with an exact bound:
each remaining prime removes at most its largest class of the primes still
alive).  Each vector is one progression N = N0 (mod M) with the same M.

Why: a member of a progression succeeds with probability about
exp(-p * |residual|), so vectors with equal residual size are equally good,
and there are thousands of them within a few primes of the best.  Scanning
V of them to the same height reaches a V times smaller N for the same
number of candidates (vscan.py).  The greedy vector is usually not the best.

Output: a list of specs {name, Q, cover, residual, N0, M}, smallest residual
set first.
"""
import json
import sys

import numpy as np
from sympy import primerange
from sympy.ntheory.modular import crt


def enumerate_vectors(Q, rs, limit):
    """[(residual size, [(r, a), ...])] for all nonzero residue vectors with residual size <= limit."""
    primes = np.array(list(primerange(3, Q)), dtype=np.int64)
    res = {r: primes % r for r in rs}
    out = []

    def dfs(i, alive, vec):
        if i == len(rs):
            out.append((int(alive.sum()), list(vec)))
            return
        counts = [np.bincount(res[r][alive], minlength=r) for r in rs[i:]]
        if int(alive.sum()) - sum(int(c[1:].max()) for c in counts) > limit:
            return
        r, cnt = rs[i], counts[0]
        for a in sorted(range(1, r), key=lambda a: -cnt[a]):
            vec.append((r, a))
            dfs(i + 1, alive & (res[r] != a), vec)
            vec.pop()

    dfs(0, np.ones(len(primes), bool), [])
    out = [(n, v) for n, v in out if n <= limit]
    out.sort()
    return primes, res, out


def main():
    spec = json.load(open(sys.argv[1]))
    spec = spec[0] if isinstance(spec, list) else spec
    D = int(sys.argv[2])
    Q, rs = spec["Q"], sorted(int(r) for r, _ in spec["cover"])
    base = len(spec["residual"])
    primes, res, vectors = enumerate_vectors(Q, rs, base + D)
    sizes = [n for n, _ in vectors]
    print(f"cover primes {rs}; greedy residual {base}; {len(vectors)} vectors with residual <= {base + D}: "
          + ", ".join(f"{sizes.count(n)} with {n}" for n in sorted(set(sizes))))
    M = 2
    for r in rs:
        M *= r
    specs = []
    for idx, (n, vec) in enumerate(vectors):
        N0 = int(crt([2] + [r for r, _ in vec], [0] + [a for _, a in vec])[0])
        alive = np.ones(len(primes), bool)
        for r, a in vec:
            alive &= res[r] != a
        U = [int(q) for q in primes[alive]]
        assert len(U) == n and N0 % 2 == 0 and all((N0 - a) % r == 0 for r, a in vec)
        specs.append({"name": f"{spec['name']}_v{idx}", "Q": Q, "cover": [[r, a] for r, a in vec],
                      "residual": U, "N0": str(N0), "M": str(M)})
    json.dump(specs, open(sys.argv[3], "w"))


if __name__ == "__main__":
    main()

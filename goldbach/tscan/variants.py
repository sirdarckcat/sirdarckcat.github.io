#!/usr/bin/env python3
"""All near-optimal residue vectors on a cover's primes, as scan specs.

    python3 variants.py base_spec.json D out.json [max_vectors [tail]]

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
set first.  With max_vectors the search stops after that many vectors (for
covers with many primes, where the full list is astronomically long); the
result is then a sample, not the complete set.  With tail only the tail
largest cover primes are varied and the others keep the base residues,
which is what makes the search finish on covers of 20 or more primes.
"""
import json
import sys

import numpy as np
from sympy import primerange
from sympy.ntheory.modular import crt


def enumerate_vectors(Q, rs, limit, max_vectors=None, fixed=()):
    """[(residual size, [(r, a), ...])] for all nonzero residue vectors with residual size <= limit
    (or the first max_vectors of them in depth-first order)."""
    primes = np.array(list(primerange(3, Q)), dtype=np.int64)
    res = {r: primes % r for r in rs}
    out = []
    fixed = dict(fixed)                     # prime -> residue it must keep

    def dfs(i, alive, vec):
        if max_vectors is not None and len(out) >= max_vectors:
            return
        n = int(alive.sum())
        if i == len(rs):
            out.append((n, list(vec)))
            return
        counts = [np.bincount(res[r][alive], minlength=r) for r in rs[i:]]
        # the later primes remove at most their largest class of the primes alive now
        later = sum(int(c[1:].max()) for c in counts[1:])
        r, cnt = rs[i], counts[0]
        for a in ([fixed[r]] if r in fixed else sorted(range(1, r), key=lambda a: -cnt[a])):
            if n - int(cnt[a]) - later > limit:
                break                       # classes come in decreasing size: the rest fail too
            vec.append((r, a))
            dfs(i + 1, alive & (res[r] != a), vec)
            vec.pop()

    dfs(0, np.ones(len(primes), bool), [])
    assert all(n <= limit for n, _ in out)
    out.sort()
    return primes, res, out


def main():
    spec = json.load(open(sys.argv[1]))
    spec = spec[0] if isinstance(spec, list) else spec
    D = int(sys.argv[2])
    Q, rs = spec["Q"], sorted(int(r) for r, _ in spec["cover"])
    base = len(spec["residual"])
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else None
    tail = int(sys.argv[5]) if len(sys.argv) > 5 else len(rs)
    fixed = {int(r): int(a) % int(r) for r, a in spec["cover"] if int(r) in rs[:len(rs) - tail]}
    primes, res, vectors = enumerate_vectors(Q, rs, base + D, cap, fixed)
    sizes = [n for n, _ in vectors]
    print(f"cover primes {rs}; greedy residual {base}; {len(vectors)} vectors"
          f"{' (search capped)' if cap and len(vectors) >= cap else ''} with residual <= {base + D}: "
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

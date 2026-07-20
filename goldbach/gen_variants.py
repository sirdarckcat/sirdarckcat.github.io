"""Generate independent search variants from a base cover.

Perturbing the residues of a few mid-size moduli to their next-best
classes yields a different CRT value N0 (same M, slightly larger
residual set).  Each variant is an independent progression, so R
variants searched to depth K give the same total success probability as
one progression searched to R*K, while keeping k -- and hence
digits(N) = digits(k*M) -- small.

Usage: gen_variants.py base_spec.json out_specs.json n_variants [kmax] [ceiling]
"""

import itertools
import json
import math
import sys

import numpy as np
from sympy import primerange

import cover as C

LN10 = math.log(10)


def variants(base, n_want, kmax=None, ceiling=None, max_extra_res=12):
    Q = base["Q"]
    targets = np.array(list(primerange(3, Q)), dtype=np.int64)
    chosen = {int(r): int(a) for r, a in base["cover"]}
    cnt = np.zeros(len(targets), dtype=np.int16)
    for r, a in chosen.items():
        cnt += (targets % r) == a
    base_res = int((cnt == 0).sum())
    boost = base["boost"]

    # for each modulus, alternative residues ranked by coverage of the
    # *full* target set restricted to what only this modulus covers
    alts = []  # (extra_residuals, r, a_alt)
    for r, a in chosen.items():
        m = targets % r
        only = (cnt == 1) & (m == a)          # exposed if residue moves
        cover_now = np.bincount(m[cnt == 0], minlength=r)
        exposed_by = np.bincount(m[only], minlength=r)
        for a2 in np.argsort(-(cover_now))[:6]:
            a2 = int(a2)
            if a2 == a:
                continue
            extra = int(only.sum()) - int(cover_now[a2])
            alts.append((extra, r, a2))
    alts.sort()
    alts = [x for x in alts if x[0] <= max_extra_res]

    out = []
    seen = set()
    # single swaps first, then pairs of the cheapest swaps
    combos = [(i,) for i in range(len(alts))] + \
        [c for c in itertools.combinations(range(min(len(alts), 40)), 2)]
    for combo in combos:
        rs = [alts[i][1] for i in combo]
        if len(set(rs)) < len(rs):
            continue
        newc = dict(chosen)
        extra = 0
        for i in combo:
            _, r, a2 = alts[i]
            newc[r] = a2
            extra += alts[i][0]
        key = tuple(sorted(newc.items()))
        if key in seen:
            continue
        seen.add(key)
        cnt2 = np.zeros(len(targets), dtype=np.int16)
        for r, a in newc.items():
            cnt2 += (targets % r) == a
        residual = [int(q) for q in targets[cnt2 == 0]]
        covr = sorted((int(r), int(a)) for r, a in newc.items())
        N0, M = C.crt(covr)
        D, E = C.self_consistent_D(base["m_digits"], len(residual), boost)
        spec = {"Q": Q, "cover": covr, "residual": residual, "boost": boost,
                "m_digits": base["m_digits"], "E": E, "n_digits_est": D,
                "N0": str(N0), "M": str(M),
                "name": f"{base['name']}_v{len(out)}"}
        if kmax:
            spec["kmax"] = kmax
        if ceiling:
            spec["ceiling_digits"] = ceiling
        out.append(spec)
        if len(out) >= n_want:
            break
    return out


def main():
    base = json.load(open(sys.argv[1]))
    n = int(sys.argv[3])
    kmax = int(sys.argv[4]) if len(sys.argv) > 4 else None
    ceiling = int(sys.argv[5]) if len(sys.argv) > 5 else None
    specs = [base] + variants(base, n - 1, kmax=kmax, ceiling=ceiling)
    if kmax:
        specs[0]["kmax"] = kmax
    if ceiling:
        specs[0]["ceiling_digits"] = ceiling
    json.dump(specs, open(sys.argv[2], "w"))
    es = [s["E"] for s in specs]
    print(f"wrote {len(specs)} specs to {sys.argv[2]}; "
          f"E range {min(es):.2f}..{max(es):.2f} "
          f"|U| range {min(len(s['residual']) for s in specs)}.."
          f"{max(len(s['residual']) for s in specs)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Turn covers found by ptcover into search specs (the JSON format of goldbach/phd/campaign3).

    python3 make_specs.py Q name kmax covers.txt out.json [max_covers] [kmax_residual]

covers.txt holds lines "COVER k r:a r:a ..." or "BEST r:a r:a ..." (ptcover output).  Every cover is checked
from scratch: residues nonzero, residual recomputed, N0 = the even number below M = 2*prod(r) with N0 = a (mod r).
The covers are sorted by residual size; identical ones are dropped.
"""
import json, math, sys
from functools import reduce

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

def crt_even(cover):
    M, x = 2, 0
    for r, a in cover:
        t = ((a - x) * pow(M, -1, r)) % r
        x += M * t; M *= r
    return x, M

def spec(Q, rows, cover, name, kmax):
    assert all(0 < a < r for r, a in cover) and len({r for r, _ in cover}) == len(cover)
    residual = [q for q in rows if all(q % r != a for r, a in cover)]
    N0, M = crt_even(cover)
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cover)
    boost = 2.0
    for r, _ in cover: boost *= r / (r - 1)
    nd = math.log10(M) + math.log10(kmax)
    return {"Q": Q, "cover": [list(c) for c in cover], "residual": residual, "boost": boost, "m_digits": math.log10(M),
            "E": len(residual) * boost / (nd * math.log(10)), "n_digits_est": nd, "N0": str(N0), "M": str(M), "name": name,
            "kmax": kmax, "stop_on_success": True}

if __name__ == "__main__":
    Q, name, kmax, src, dst = int(sys.argv[1]), sys.argv[2], int(float(sys.argv[3])), sys.argv[4], sys.argv[5]
    limit = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    kcap = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
    rows = [q for q in primes_upto(Q - 1) if q > 2]
    seen, covers = set(), []
    for line in open(src):
        f = line.split()
        if not f or f[0] not in ("COVER", "BEST"): continue
        cov = tuple(tuple(map(int, x.split(":"))) for x in f[(2 if f[0] == "COVER" else 1):])
        if cov in seen: continue
        seen.add(cov); covers.append(cov)
    specs = [spec(Q, rows, c, "", kmax) for c in covers]
    specs = [s for s in specs if len(s["residual"]) <= kcap]
    specs.sort(key=lambda s: len(s["residual"]))
    specs = specs[:limit]
    for i, s in enumerate(specs): s["name"] = f"{name}_v{i}"
    json.dump(specs, open(dst, "w"))
    ks = [len(s["residual"]) for s in specs]
    print(f"{len(specs)} specs written to {dst}: residual sizes {min(ks)}..{max(ks)}, E {specs[0]['E']:.3f}..{specs[-1]['E']:.3f}, "
          f"M has {specs[0]['m_digits']:.2f} digits, N below 10^{specs[0]['n_digits_est']:.2f} for k < {kmax}")

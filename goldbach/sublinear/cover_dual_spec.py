#!/usr/bin/env python3
"""A cover (classes of odd prime moduli) as a spec for goldbach/search.py: the progression N = N0 + k M of even numbers
in the cover's classes, and the rows the cover leaves (odd primes q < Q in no class: N - q is divisible by no modulus).

    python3 cover_dual_spec.py cover.txt Q digits name out.json [kstart [kmax]]

cover.txt: a line "BEST r:a r:a ..." or "COVER k r:a ..." (the last such line is used), as ptcover prints them.
"""
import sys, json
def primes(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\0\0"
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
cover_file, Q, digits, name, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
cover = None
for l in open(cover_file):
    t = l.split()
    if t and t[0] in ("BEST", "COVER"):
        cover = [tuple(map(int, u.split(":"))) for u in t[1:] if ":" in u]
assert cover and all(0 < a < r for r, a in cover) and len(set(r for r, a in cover)) == len(cover)
ps = set(primes(max(r for r, a in cover))); assert all(r in ps and r > 2 for r, a in cover)
M = 2; N0 = 0
for r, a in cover:
    t = ((a - N0) * pow(M, -1, r)) % r; N0 += t * M; M *= r
assert N0 % 2 == 0 and all(N0 % r == a for r, a in cover) and 0 <= N0 < M
rows = [q for q in primes(Q - 1) if q > 2 and all(q % r != a for r, a in cover)]
kcap = (10 ** digits - 1 - N0) // M                    # members k = 0 .. kcap are below 10^digits
spec = {"name": name, "N0": str(N0), "M": str(M), "Q": Q, "residual": rows, "cover": [list(c) for c in cover],
        "fast_verify": True, "ceiling_digits": digits, "kstart": int(sys.argv[6]) if len(sys.argv) > 6 else 0,
        "kmax": int(sys.argv[7]) if len(sys.argv) > 7 else kcap + 1}
json.dump(spec, open(out, "w"))
print(f"{name}: {len(cover)} moduli, M has {len(str(M))} digits, {kcap + 1} members below 10^{digits}, {len(rows)} rows below {Q}")

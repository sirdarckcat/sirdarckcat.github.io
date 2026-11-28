#!/usr/bin/env python3
"""Turn covers found by ptcover or covergen into search specs (the JSON format of goldbach/phd/campaign3).

    python3 make_specs.py Q name kmax covers.txt out.json [max_covers] [kmax_residual] [ledger.txt]
        (kmax "auto": each spec gets the largest kmax that keeps N below 10^200, for modulus sets other than the 88;
         kmax "top32": for an engine with 32-bit k.  kmax is 2^32 and, when more than 2^32 members fit below 10^200,
         N0 is moved up by a multiple of M so that k = 2^32 - 1 is the last member below 10^200: the k range then ends
         at the top of the 200-digit numbers, where primes are rarest.  The spec records the move as "k_shift"
         (N0 - k_shift * M is the residue below M), and its ledger key is that of the moved N0, so a cover handed out
         before with its low range can be handed out again with its top range)
    python3 make_specs.py --ledger ledger.txt file [more files ...]

covers.txt holds lines "COVER k r:a r:a ..." or "BEST r:a r:a ..." (ptcover / covergen output).  Every cover is
checked from scratch: residues nonzero, residual recomputed, N0 = the even number below M = 2*prod(r) with
N0 = a (mod r).  Identical covers are dropped; the covers are taken in the order of the residual size the sampler
reported, that size is recomputed for each, and the first max_covers specs with at most kmax_residual rows are kept.

ledger.txt (optional) has one line per vector already handed out: the first 20 hex digits of the SHA-256 of the
decimal N0.  A cover whose N0 is in the ledger is skipped and the N0 of every spec written is appended, so batches
made with the same ledger never repeat a vector.  The second form adds the vectors of existing files: spec files
(JSON lists), pool files of goldbach/phd/cap200 (JSON with "mods" and "pool") or cover lines (any other file).
"""
import hashlib, json, math, sys
try:
    import numpy as np
except ImportError:                      # the pure Python path is the same computation, about 100 times slower
    np = None

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

def key(N0): return hashlib.sha256(str(N0).encode()).hexdigest()[:20]

_rows_np, _rowmod = None, {}
def residual_of(rows, cover):
    global _rows_np
    if np is None: return [q for q in rows if all(q % r != a for r, a in cover)]
    if _rows_np is None: _rows_np = np.array(rows, dtype=np.int64)
    covered = np.zeros(len(rows), dtype=bool)
    for r, a in cover:
        if r not in _rowmod: _rowmod[r] = (_rows_np % r).astype(np.int32)
        covered |= _rowmod[r] == a
    return _rows_np[~covered].tolist()

def spec(Q, rows, cover, name, kmax):
    assert all(0 < a < r for r, a in cover) and len({r for r, _ in cover}) == len(cover)
    residual = residual_of(rows, cover)
    N0, M = crt_even(cover)
    shift = 0
    if kmax == "top32":
        kmax = (10 ** 200 - 1 - N0) // M + 1
        if kmax > 2 ** 32: shift = kmax - 2 ** 32; N0 += shift * M; kmax = 2 ** 32
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cover)
    if kmax is None: kmax = (10 ** 200 - 1 - N0) // M + 1        # "auto": every member below 10^200
    boost = 2.0
    for r, _ in cover: boost *= r / (r - 1)
    nd = math.log10(M) + math.log10(kmax + shift)             # digits of the largest member
    return {"Q": Q, "cover": [list(c) for c in cover], "residual": residual, "boost": boost, "m_digits": math.log10(M),
            "E": len(residual) * boost / (nd * math.log(10)), "n_digits_est": nd, "N0": str(N0), "M": str(M), "name": name,
            "kmax": kmax, "ceiling_digits": len(str(N0 + (kmax - 1) * M)), "stop_on_success": True, **({"k_shift": shift} if shift else {})}

if __name__ == "__main__":
    if sys.argv[1] == "--ledger":
        have = set(open(sys.argv[2]).read().split()) if __import__("os").path.exists(sys.argv[2]) else set()
        new = []
        def n0s(f):
            try: d = json.load(open(f))
            except ValueError: d = None
            if isinstance(d, list):
                for s in d: yield int(s["N0"])
            elif isinstance(d, dict):
                for _, classes in d["pool"]: yield crt_even(sorted(zip(d["mods"], classes)))[0]
            else:
                for line in open(f):
                    t = line.split()
                    if t and t[0] in ("COVER", "BEST"):
                        yield crt_even(sorted(tuple(map(int, x.split(":"))) for x in t[(2 if t[0] == "COVER" else 1):]))[0]
        for f in sys.argv[3:]:
            for N0 in n0s(f):
                h = key(N0)
                if h not in have: have.add(h); new.append(h)
        with open(sys.argv[2], "a") as g: g.write("".join(h + "\n" for h in new))
        print(f"{len(new)} vectors added to {sys.argv[2]} ({len(have)} in all)"); sys.exit()
    Q, name, src, dst = int(sys.argv[1]), sys.argv[2], sys.argv[4], sys.argv[5]
    kmax = None if sys.argv[3] == "auto" else "top32" if sys.argv[3] == "top32" else int(float(sys.argv[3]))
    limit = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    kcap = int(sys.argv[7]) if len(sys.argv) > 7 else 10 ** 9
    ledger = sys.argv[8] if len(sys.argv) > 8 else None
    used = set()
    if ledger:
        try: used = set(open(ledger).read().split())
        except FileNotFoundError: pass
    rows = [q for q in primes_upto(Q - 1) if q > 2]
    seen, covers = set(), []
    for line in open(src):
        f = line.split()
        if not f or f[0] not in ("COVER", "BEST"): continue
        cov = tuple(tuple(map(int, x.split(":"))) for x in f[(2 if f[0] == "COVER" else 1):])
        if cov in seen: continue
        seen.add(cov); covers.append((int(f[1]) if f[0] == "COVER" else 0, len(covers), cov))
    covers = [c for _, _, c in sorted(covers)]            # by the residual size the sampler reported
    specs, skipped, new = [], 0, []
    for c in covers:
        if len(specs) >= limit: break
        s = spec(Q, rows, c, "", kmax)
        if len(s["residual"]) > kcap: continue
        h = key(int(s["N0"]))
        if h in used: skipped += 1; continue
        used.add(h); new.append(h); specs.append(s)
    if not specs: sys.exit(f"no new spec: {len(covers)} covers read, {skipped} already in the ledger")
    specs.sort(key=lambda s: len(s["residual"]))
    for i, s in enumerate(specs): s["name"] = f"{name}_v{i}"
    json.dump(specs, open(dst, "w"))
    if ledger:
        with open(ledger, "a") as g: g.write("".join(h + "\n" for h in new))
    ks = [len(s["residual"]) for s in specs]
    print(f"{len(specs)} specs written to {dst}: residual sizes {min(ks)}..{max(ks)}, E {specs[0]['E']:.3f}..{specs[-1]['E']:.3f}, "
          f"M has {specs[0]['m_digits']:.2f} digits, N below 10^{specs[0]['n_digits_est']:.2f} for k < {specs[0]['kmax']}"
          + (f"; {skipped} covers skipped as already in {ledger}" if ledger else ""))

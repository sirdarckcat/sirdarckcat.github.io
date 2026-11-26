#!/usr/bin/env python3
"""The feeder (selection, CSR, statistics) against numpy: the argsort of search.run_block, the alive matrix, the hit mass, and
the reference numbers of the GPU session for the 850-row cover (k0 = 4,293,885,952, L = 32,768, B = 1e6).

    python3 test_feeder.py [--cover path/to/spec_q122000_k850.json]
"""
import argparse, hashlib, json, math, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from sieve200 import Feeder, Sieve200


def reference(sv, bits_feeder, fb_list, counts_k0, L, f, p_est):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", default=os.path.join(HERE, "..", "phd", "campaign3", "base_spec.json"))
    a = ap.parse_args()
    spec = json.load(open(a.cover))
    spec = spec[0] if isinstance(spec, list) else spec
    U = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
    cover = [r for r, _ in spec["cover"]]
    N0, M = int(spec["N0"]), int(spec["M"])
    ok = True
    print(f"cover {os.path.basename(a.cover)}: {len(U)} rows")
    # numpy reference of a whole window, then every block compared
    for B, logK, L, k0 in ((200003, 17, 1 << 15, 5 * (1 << 17) + 12345 * 0), (1000000, 18, 1 << 16, 4293885952 - 4293885952 % (1 << 18)), (50021, 16, 1 << 14, 1 << 31)):
        for f in (0.97, 0.5, 0.0, 0.999, 0.9999):
            fd = Feeder(N0, M, U, B=B, L=L, logK=logK, f=f, p_est=0.055, exclude=cover)
            blocks = fd.window(k0)
            counts, bits = fd.sv.block(k0)                 # the same window again, for the reference
            alive = fd.sv.alive(bits)
            assert np.array_equal(alive.sum(axis=0), counts)
            bad = 0
            for b, fb in enumerate(blocks):
                cb = counts[b * L:(b + 1) * L].astype(np.int64)
                keep = int(math.ceil(L * (1.0 - f)))
                order = np.argsort(cb, kind="stable")[:keep]
                w = (1.0 - 0.055) ** cb.astype(np.float64)
                same = (np.array_equal(fb.k, order.astype(np.uint64) + np.uint64(k0 + b * L)) and np.array_equal(fb.cnt, cb[order].astype(np.uint16))
                        and fb.alive_total == int(cb.sum()) and abs(fb.hm_all - w.sum()) <= 1e-12 * w.sum()
                        and abs(fb.hm_kept - w[order].sum()) <= 1e-12 * max(w[order].sum(), 1e-300))
                if same:
                    for i in random.Random(b).sample(range(len(order)), min(len(order), 40)) if len(order) else []:
                        r = fb.rows[fb.offs[i]:fb.offs[i + 1]]
                        col = np.nonzero(alive[:, b * L + int(order[i])])[0]
                        same &= np.array_equal(r, col)
                    same &= int(fb.offs[-1]) == len(fb.rows) == int(cb[order].sum())
                bad += not same
            print(f"  B={B:8d} K=2^{logK} L=2^{int(math.log2(L))} f={f:<7} k0={k0:<11d} {len(blocks)} blocks, selected {len(blocks[0].k):6d}: {'identical' if not bad else f'{bad} DIFFERENT'}")
            ok &= bad == 0
    # the GPU session's reference numbers for their 850-row cover (when that cover is the one given)
    if len(U) == 850:
        fd = Feeder(N0, M, U, B=1000000, L=1 << 15, logK=15, f=0.97, p_est=0.055, exclude=cover)
        fb = fd.window(4293885952)[0]
        counts, _ = fd.sv.block(4293885952)
        sha = hashlib.sha256(counts.astype("<u2").tobytes()).hexdigest()
        ref = dict(alive=12459413, sha="704be04a5a2297f46f8b11f0c963ae1313a942e64501f7dd1dc5fec9f7b96ec4", nsel=984, js=[24236, 12679, 14788, 27793, 11914],
                   cnts=[323, 326, 328, 328, 329], maxkept=354)
        good = (fb.alive_total == ref["alive"] and sha == ref["sha"] and len(fb.k) == ref["nsel"]
                and [int(k) - 4293885952 for k in fb.k[:5]] == ref["js"] and fb.cnt[:5].tolist() == ref["cnts"] and int(fb.cnt.max()) == ref["maxkept"]
                and abs(fb.hm_kept - 2.899909e-06) < 2e-12 and abs(fb.hm_all - 2.059896e-05) < 2e-11)
        print(f"  GPU session's reference (850 rows, k0=4293885952, f=.97): alive {fb.alive_total}, kept {len(fb.k)}, hm {fb.hm_kept:.6e}/{fb.hm_all:.6e}: {'identical' if good else 'DIFFERENT'}")
        ok &= good
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

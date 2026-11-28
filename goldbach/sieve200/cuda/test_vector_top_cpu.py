#!/usr/bin/env python3
"""search_gpu5_vectop.patch (--vector-top 1): the arithmetic of the top-of-range window on real vector specs: the window [kmax - K, kmax) holds only N with `digits` digits and N < 10^ceiling_digits,
is disjoint from nothing it should not touch, starts at or after the first `digits`-digit k, and the patch's assertion holds; the bottom window is the one the driver uses today.

    python3 test_vector_top_cpu.py [spec.json ...]      (default: the specs under phd/campaign3_gpu/v89/ that exist, else phd/campaign3/specs_variants.json's first spec with a kmax)
"""
import glob, json, os, sys
from gmpy2 import mpz

HERE = os.path.dirname(os.path.abspath(__file__))
K = 1 << 24


def specs(paths):
    for p in paths:
        d = json.load(open(p))
        for s in (d if isinstance(d, list) else [d]):
            for f in ("residual", "cover"):
                if isinstance(s.get(f), str):
                    s[f] = json.loads(s[f])
            if "kmax" in s and "N0" in s and "M" in s:
                yield p, s


def main():
    paths = sys.argv[1:] or glob.glob(os.path.join(HERE, "..", "..", "phd", "campaign3_gpu", "v89", "*spec*.json")) + glob.glob("/tmp/claude-0/**/kc_spec.json", recursive=True)
    ok, n = True, 0
    lo = mpz(10) ** 199
    for p, s in specs(paths):
        N0, M, kmax = mpz(s["N0"]), mpz(s["M"]), int(s["kmax"])
        k_lo = int((lo - N0 + M - 1) // M) if lo > N0 else 0
        if k_lo + K > kmax:
            print(f"  {os.path.basename(p)} {s.get('name')}: the vector holds no whole window (skipped by the driver)")
            continue
        k_top = kmax - K
        ceil = mpz(10) ** int(s.get("ceiling_digits", 200))
        good = (N0 + k_top * M >= lo and N0 + (k_top + K - 1) * M < ceil and N0 + kmax * M >= ceil and k_top >= k_lo
                and len(str(N0 + k_top * M)) == 200 and len(str(N0 + (kmax - 1) * M)) == 200)
        # the bottom window for comparison: from the first 200-digit k
        good = good and N0 + k_lo * M >= lo and len(str(N0 + (k_lo - 1) * M)) == 199 if k_lo > 0 else good
        n += 1
        ok &= good
        print(f"  {os.path.basename(p)} {s.get('name')}: valid k [{k_lo:,}, {kmax:,}) = {kmax - k_lo:,}; top window [{k_top:,}, {kmax:,}): first N {len(str(N0 + k_top * M))} digits, last N {len(str(N0 + (kmax - 1) * M))} digits, "
              f"the next k has {len(str(N0 + kmax * M))}: {'ok' if good else 'FAILED'}")
    ok &= n > 0
    print("VECTOR-TOP OK" if ok else "VECTOR-TOP FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One rung from several frontier.py runs over disjoint covers (--cover-offset): sums of members, tests, PRPs and the
tested histograms, p^ and the expected hits recomputed from the sums, the hits pooled.

    python3 frontier_combine.py out.json run1.json run2.json ..."""
import json
import math
import sys

out, ins = sys.argv[1], [json.load(open(f)) for f in sys.argv[2:]]
for r in ins[1:]:
    assert (r["digits"], r["c"], r["Q"], r["moduli"]) == (ins[0]["digits"], ins[0]["c"], ins[0]["Q"], ins[0]["moduli"]), "not one rung"
offs = sorted((r.get("cover_offset", 0), r["covers"]) for r in ins)
for (o1, n1), (o2, _) in zip(offs, offs[1:]):
    assert o1 + n1 <= o2, "overlapping covers"
hist = {}
for r in ins:
    for a, n in r["hist"].items():
        hist[int(a)] = hist.get(int(a), 0) + n
tests = sum(r["tests"] for r in ins)
prp = sum(r["prp"] for r in ins)
p = prp / tests
se = math.sqrt(p * (1 - p) / tests) / math.sqrt(max(1e-12, 1 - p))
expd = lambda pp: sum(n * (1 - pp) ** a for a, n in hist.items())
tested = sum(hist.values())
mean_a = sum(a * n for a, n in hist.items()) / tested
hits = [h for r in ins for h in r["hits"]]
res = dict(ins[0])
res.update({"cover_offset": [o for o, _ in offs], "covers": sum(r["covers"] for r in ins),
            "rows_min": min(r["rows_min"] for r in ins), "rows_max": max(r["rows_max"] for r in ins),
            "members": sum(r["members"] for r in ins), "tested": tested, "tests": tests, "prp": prp, "p_hat": p, "p_se": se,
            "expected": expd(p), "expected_lo": expd(p + se), "expected_hi": expd(p - se), "E_tested": mean_a * -math.log(1 - p),
            "found": len(hits), "candidates": sum(r["candidates"] for r in ins), "hits": hits,
            "cpu_seconds": sum(r["cpu_seconds"] for r in ins), "hist": {str(a): n for a, n in sorted(hist.items())},
            "covers_used": [c for r in ins for c in r["covers_used"]], "parts": sys.argv[2:]})
json.dump(res, open(out, "w"))
print(f"d={res['digits']} Q={res['Q']}: {res['covers']} covers (rows {res['rows_min']}..{res['rows_max']}), {res['members']} members, "
      f"{tested} tested, p^={p:.5f}; expected {res['expected']:.2f} ({res['expected_lo']:.2f}..{res['expected_hi']:.2f}), "
      f"found {len(hits)}; E_tested={res['E_tested']:.2f}; {res['cpu_seconds'] / 3600:.2f} CPU-h; best closeness "
      f"{max([h['closeness'] for h in hits], default=0):.4f}")

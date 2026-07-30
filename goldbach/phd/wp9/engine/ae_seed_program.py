# WP9 seed program for the AlphaEvolve generative tier.
#
# CONTRACT (see harness.md, THREAT-MODEL section): this program's ONLY job
# is to print candidate certificate schemas as JSON lines on stdout. It must
# never compute kills, never import the scorer, never read the residual set,
# and never report a fitness. All grading happens outside, in a fresh
# interpreter, with the trusted scorer. Programs that violate the contract
# simply score 0 because nothing they print is believed.
#
# The research question being evolved: is there a certificate schema in the
# grammar L that certifies MANY prime offsets q < Q = 122,000 composite for
# a constructible family of N < 10^200, at a marginal design-entropy cost
# below covering's measured endgame (~1.01 nats per residual kill)? The
# Divisor-Paradigm Closure Theorem (wp9_closure_theorem.md) predicts none
# exists; 13,661 hand-enumerated schemas found none. Your job is to find a
# counterexample, or to sharpen the empirical ceiling.
#
# Grammar (params must match exactly; anything else scores 0):
#   {"family":"Congruence",     "params":{"d":int>=2,"a":int}}
#   {"family":"PolyImage",      "params":{"k":2..4,"a":int>=1,"c":int>=1}}
#   {"family":"ExpFamily",      "params":{"a":2..7,"j":int>=1,"c":int}}
#   {"family":"MultiPolyBin",   "params":{"A":[a,b,c]}}
#   {"family":"MultiPolyQuart", "params":{"A":[a,b,c],"B":[a,b,c]}}
#   {"family":"Cyclotomic",     "params":{"n":3..500}}
#   {"family":"Compose",        "params":{"parts":[<schema>,<schema>]}}
#
# Known frontier (all REJECTED so far): PolyImage tops out near 113
# certifiable offsets (value-set ceiling ~Q^(1/k)); ExpFamily costs 3.1-4.2
# nats per residual kill (one offset per order-condition); products of two
# quadratic forms die on an enumeration wall measured at height^0.5-0.74;
# Congruence IS the covering baseline and is scored as such (fitness 0).
#
# Emit at most 4000 schemas per run. Duplicates are harmless but wasted.

import json

# EVOLVE-BLOCK-START
def propose_schemas():
    """Return a list of candidate certificate schemas (dicts).

    Baseline strategy: sweep the shift parameter of the square family
    N = m^2 - c, which is the best univariate mechanism known (WP7-P2:
    c = 398 certifies 113 offsets below 10^5). Also probe a few cubic
    shifts and a couple of composed pairs.

    Evolve this function. Ideas the closure argument has NOT ruled out at
    the grammar's edge: compositions that restrict a polynomial image to a
    congruence class so the two mechanisms' offset sets reinforce instead
    of overlapping; exponential families whose order conditions are chosen
    to hit many residual offsets at once; cyclotomic splittings at highly
    composite n where phi(n) stays small.
    """
    out = []
    for c in range(1, 1200):
        out.append({"family": "PolyImage", "params": {"k": 2, "a": 1, "c": c}})
    for c in range(1, 200):
        out.append({"family": "PolyImage", "params": {"k": 3, "a": 1, "c": c}})
    for n in (105, 165, 195, 210, 231, 255, 273, 285, 315, 330):
        out.append({"family": "Cyclotomic", "params": {"n": n}})
    for j in (1, 3, 5):
        for c in (-1, 1):
            out.append({"family": "ExpFamily", "params": {"a": 2, "j": j, "c": c}})
    for c1, c2 in ((398, 4686), (398, 1510), (4686, 1261)):
        out.append({"family": "Compose", "params": {"parts": [
            {"family": "PolyImage", "params": {"k": 2, "a": 1, "c": c1}},
            {"family": "PolyImage", "params": {"k": 2, "a": 1, "c": c2}},
        ]}})
    return out
# EVOLVE-BLOCK-END


if __name__ == "__main__":
    for schema in propose_schemas()[:4000]:
        print(json.dumps(schema))

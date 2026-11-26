# The forecast on the 170,000 design with what survives of the three cost-side items (research, 25 Nov), from item3_keep.py's
# model: E[final record] and P(final >= 180k, 190k, 200k), every tested member's g counted, floor 160,357.
#   - item 1 (two-stage count): its selection numbers agree (item1_two_stage.py), but its GPU design was withdrawn by its author
#     (4104ae5: the filter costs an L2 lookup a mark), so it is not in the package;
#   - item 2 (carry-over): built and CPU-proven by uarch (fe27cbe, 4c82a0b); counted two ways: removing the waste only (the tail and
#     the gaps already hidden, as the GPU session's control-stream run suggests) or the waste and the tail of 0.175 s a batch;
#   - item 3 (keep): re-optimised for E[final record] in each case.
# Sensitivity, not in the package: the sieve 20% faster (pass A at its integer floor, uarch's estimate, not checkable from here).
#   python3 forecast.py
import math, numpy as np
import item3_keep as m

def cost(kappa, carry, tail_counts, sieve=1.0):
    bulk = (m.F15 - m.TAIL) * (1 - m.W15) * kappa / m.K0
    if carry: F = bulk + (m.TAIL if not tail_counts else 0.0)
    else: F = bulk / (1 - m.waste(kappa)) + m.TAIL
    return m.batch(F, m.S0 * sieve) / m.batch(m.F15, m.S0)

def fc(kappa, carry, tail_counts, sieve=1.0):
    m.cost = lambda k, model: cost(k, carry, tail_counts, sieve)       # route item3_keep.forecast through this cost
    return m.forecast(kappa, "X")

cases = [("today (keep 1.5%, rounds as now)", False, False, 1.0, [0.015]),
         ("keep re-optimised, rounds as now", False, False, 1.0, None),
         ("carry-over (waste only) + keep re-optimised", True, False, 1.0, None),
         ("carry-over (waste and tail) + keep re-optimised", True, True, 1.0, None),
         ("sensitivity: the last, with the sieve 20% faster", True, True, 0.8, None)]
fine = np.exp(np.linspace(np.log(0.003), np.log(0.03), 120))
print("configuration | keep | design hits at 170k | package (nats) | E[final record] | P(>= 180k) | P(>= 190k) | P(>= 200k)")
for name, carry, tc, sv, ks in cases:
    ks = ks or fine
    k = max(ks, key=lambda k: fc(k, carry, tc, sv)["E"]); r = fc(k, carry, tc, sv)
    print(f"{name} | {100 * k:.2f}% | {r['hits']:.3f} | {math.log(r['hits'] / 1.90):+.3f} | {r['E']:,.0f} | {100 * r['P180']:.2f}% | {100 * r['P190']:.2f}% | {100 * r['P200']:.3f}%")

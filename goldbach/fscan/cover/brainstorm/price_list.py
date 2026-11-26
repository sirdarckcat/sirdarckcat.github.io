# Card-days and fleet-days for one expected success at design Q, from the rows left by the best cover found.
# Success per full-weight member = RATIO * (1 - p)^k: p = boost / ln N at N = 10^200, RATIO = 0.89 is the fleet's
# measured expected successes per member against (1 - p)^k at Q = 140,000 (2.13e-11 against 2.39e-11).
import math
p = 11.008269598801753 / (200 * math.log(10)); RATIO = 0.89
CARD = 4.8e6 * 86400       # full-weight members a day, one RTX PRO 6000 (kernel 28, GPU feeder, 3% kept)
FLEET = 18.7e6 * 86400     # the fleet on 22 Nov 2026, 23:17Z
ROWS = {150000: 1093, 160000: 1185, 170000: 1262, 180000: 1352, 190000: 1437, 200000: 1522, 213070: 1634}
print("design Q | rows left | E = k p | success per member | card-days per success | fleet-days per success")
for Q, k in ROWS.items():
    P = RATIO * (1 - p) ** k
    print(f"{Q:7d} | {k} | {k*p:5.2f} | {P:.2e} | {1/(P*CARD):10.1f} | {1/(P*FLEET):9.2f}")

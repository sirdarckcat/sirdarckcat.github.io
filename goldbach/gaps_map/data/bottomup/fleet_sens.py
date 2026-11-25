# Same prerequisites as fleet_rates.py.
import sys, math
import numpy as np
sys.argv = ['x']
import campaign_table as ct
D, f, extra_run = ct.DESIGNS[0]
U, C, c = ct.load(f)
nbest = int((U < D).sum())
scale = (nbest + extra_run) / nbest
p = C / ct.L
kap = -math.log1p(-p)
hits = 1.90
print('P(final >= G) for the 170,000 design (1.90 design hits, no package) when the mean overshoot beyond the design level is theta times the model (theta = 1 is the table)')
print('theta | 175,000 | 180,000 | 185,000 | 190,000 | 195,000 | 200,000')
for theta in (1.0, 0.8, 1.26, 1.5, 1.58):
    out = []
    for G in (175000, 180000, 185000, 190000, 195000, 200000):
        extra = float(((U >= D) & (U < G)).sum()) * scale
        lam = hits * math.exp(-extra * kap / theta)
        out.append(100 * (1 - math.exp(-lam)))
    print('%.2f | ' % theta + ' | '.join('%.2f%%' % x for x in out))
extra200 = float(((U >= D) & (U < 200000)).sum()) * scale
print('alive rows between 170,000 and 200,000: %.1f (kappa %.5f): the model suppresses design hits by e^-%.2f at 200,000' % (extra200, kap, extra200 * kap))

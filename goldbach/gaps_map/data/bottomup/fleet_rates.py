# Needs the Opus session's campaign_table.py and covers/ (branch ccr-c6e00296-3g7fp9, commit bc7316f, goldbach/bottom_up/): copy both next to this file (cp campaign_table.py rates.py; mkdir covers).
import sys, math
import numpy as np
sys.argv = ['x']
import campaign_table as ct
D, f, extra_run = ct.DESIGNS[0]
U, C, c = ct.load(f)
nbest = int((U < D).sum())
scale = (nbest + extra_run) / nbest
p = C / ct.L
pp = p / c
lamp = -math.log1p(-pp)
def n_below(G):
    return float((U < G).sum()) * scale
def sd(n):
    return 0.9836 * math.sqrt(n * c * (1 - c))
nD = n_below(D)
E_D = ct.window_E(nD, C)
cap = ct.ND.cdf(ct.z0 + lamp * sd(nD))
def lam_rel(G):
    if G >= D:
        extra = float(((U >= D) & (U < G)).sum()) * scale
        return math.exp(-extra * -math.log1p(-p))
    nG = n_below(G)
    EG = ct.window_E(nG, C)
    capG = ct.ND.cdf(ct.z0 + lamp * sd(nG) ** 2 / sd(nD))
    return math.exp(-EG) * capG / (math.exp(-E_D) * cap)
print('design 170,000 cover (the fleet 491 family): rows below 170,000 run %.1f, exponent at 170,000 %.2f' % (nD, E_D))
print('threshold G | rows below G | exponent E_G | events relative to design hits | per day at 0.19 design hits a day | days for 25 events')
for G in (135000, 140000, 145000, 150000, 155000, 157837, 160357, 165000, 170000):
    nG = n_below(G)
    EG = ct.window_E(nG, C) if G < D else E_D
    r = lam_rel(G)
    print('%9d | %8.1f | %6.2f | %8.1f | %6.2f | %5.1f' % (G, nG, EG, r, 0.19 * r, 25 / (0.19 * r)))

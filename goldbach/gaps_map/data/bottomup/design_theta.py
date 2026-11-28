# Does the best design level depend on the overshoot law? The Opus session's campaign_table.py (branch ccr-c6e00296-3g7fp9, commit bc7316f, goldbach/bottom_up/; not copied here)
# with the mean overshoot beyond the design level set to theta times the model's: a design hit at level D is decided beyond D by the cover's remaining rows in [D, G), each composite with
# probability 1 - p, so with theta the suppression exp(-extra * kappa) becomes exp(-extra * kappa / theta). The work budget is the same for every design (1.90 design hits at 170,000 as the
# fleet runs, times e^package); G below D needs the g of every tested member and does not depend on theta. theta = 1 reproduces the Opus table (E[record] 175,252 at package 0).
#   cd <dir holding campaign_table.py and covers/>; python3 <path>/design_theta.py [package_nats ...] [--full]
import sys, math
import numpy as np
full = '--full' in sys.argv
packs = [float(a) for a in sys.argv[1:] if not a.startswith('--')] or [0.0]
sys.argv = ['x']
sys.path.insert(0, '.')
import campaign_table as ct
ND, z0, R0, L = ct.ND, ct.z0, ct.R0, ct.L
pre = {}
for idx, (D, f, extra_run) in enumerate(ct.DESIGNS):
    U, C, c = ct.load(f); nbest = int((U < D).sum()); scale = (nbest + extra_run) / nbest
    p = C / L; pp = p / c; lamp = -math.log1p(-pp)
    sd = (lambda n, c=c: 0.9836 * math.sqrt(n * c * (1 - c)))
    nb = (lambda G, U=U, scale=scale: float((U < G).sum()) * scale)
    nD = nb(D); E = ct.window_E(nD, C); delta = lamp * sd(nD); cap = ND.cdf(z0 + delta)
    pre[idx] = dict(D=D, U=U, C=C, c=c, scale=scale, nD=nD, E=E, cap=cap, delta=delta, lamp=lamp, sd=sd, nb=nb, p=p)
n170 = pre[0]['nD']
for k in pre: pre[k]['cost'] = 0.26 * pre[k]['nD'] / n170 + 0.74
r0 = pre[0]; M170 = 1.90 / (math.exp(-r0['E']) * r0['cap'])
grid = np.arange(R0, 400001, 250)
Gs = (175000, 180000, 190000, 200000)
thetas = (0.8, 1.0, 1.26, 1.5, 2.0)
summary = {}
for pack in packs:
    W = M170 * r0['cost'] * math.exp(pack)
    def Lam(r, G, theta):
        M = W / r['cost']; D = r['D']
        if G >= D:
            extra = float(((r['U'] >= D) & (r['U'] < G)).sum()) * r['scale']
            return M * math.exp(-r['E']) * r['cap'] * math.exp(-extra * -math.log1p(-r['p']) / theta)
        nG = r['nb'](G); EG = ct.window_E(nG, r['C'])
        capG = ND.cdf(z0 + r['lamp'] * r['sd'](nG) ** 2 / r['sd'](r['nD']))
        return M * math.exp(-EG) * capG
    for theta in thetas:
        best = {}; lines = []
        for idx in pre:
            r = pre[idx]; D = r['D']
            hits = Lam(r, D, theta)
            ps = [100 * (1 - math.exp(-Lam(r, G, theta))) for G in Gs]
            rec = R0 + float(sum(1 - math.exp(-Lam(r, G, theta)) for G in grid)) * 250
            lines.append('%s | %.4f | ' % (format(D, ','), hits) + ' | '.join('%.3f%%' % x for x in ps) + ' | %s' % format(round(rec), ','))
            for j, G in enumerate(Gs): best[G] = max(best.get(G, (-1, 0)), (ps[j], D))
            best['rec'] = max(best.get('rec', (-1, 0)), (rec, D))
            summary[(pack, theta, D)] = rec
        summary[(pack, theta)] = best['rec'][1]
        if full:
            print('\npackage %+.2f nats (same work for every design: 1.90 design hits at 170,000 times e^package), theta = %.2f; floor %d' % (pack, theta, R0))
            print('design | design hits | ' + ' | '.join('P(>= %s)' % format(G, ',') for G in Gs) + ' | E[record]')
            print('\n'.join(lines))
            print('best design: ' + '; '.join('P(>= %s) at %s' % (format(G, ','), format(best[G][1], ',')) for G in Gs) + '; E[record] at %s' % format(best['rec'][1], ','))
print('\nDesign level with the highest E[record] (g of every tested member counted), by work budget (package, nats over today\'s 1.90 design hits at 170,000) and overshoot law theta:')
print('package | ' + ' | '.join('theta %.2f' % t for t in thetas))
for pack in packs:
    cells = []
    for t in thetas:
        b = summary[(pack, t)]; others = sorted((summary[(pack, t, D)] for D in (170000, 180000, 190000, 200000) if D != b), reverse=True)
        cells.append('%s (+%s)' % (format(b, ','), format(round(summary[(pack, t, b)] - others[0]), ',')))
    print('%+.2f | ' % pack + ' | '.join(cells))
print('(in brackets: the margin in E[record] over the next best design)')

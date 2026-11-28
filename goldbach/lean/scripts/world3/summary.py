#!/usr/bin/env python3
"""One block per run of w3: the record, and for each target the work of four orders at the line.

usage: summary.py OUT.txt [...]
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyse import parse, first_success, to_fraction, model


def kind(d):
    t = []
    if d.get('insep') == '1': t.append("N'=0")
    if d.get('trans', '-') != '-': t.append('translation-invariant')
    if d.get('scal', '-') != '-': t.append('scaling-invariant')
    if 'dM' in d and 0 <= int(d['dM']) <= 2: t.append("deg N' = %s" % d['dM'])
    return ', '.join(t) if t else 'generic'


def block(path):
    r = parse(path)
    q, n, M = r['q'], r['n'], r['members']; cut = r['cut']
    hl = r['histL']; Lmax = max(hl); p0 = r['nirr'] / M
    naive = math.log(M) / -math.log(1 - p0)
    below = 0; D = 1
    for d, c in enumerate(r['irred'], start=1):
        below += c
        if Lmax >= below: D = d + 1
    nD = sum(v for k, v in hl.items() if k >= sum(r['irred'][:D - 1]))
    top = r['TOP'][0]
    print(f"q={q} n={n} lead={'1' if r['mu'] == 1 else 'non-square' if not r['musq'] else 'square'} members={M:,}: record L={Lmax} ({hl[Lmax]} members), "
          f"D={D} ({nD} members), mean L={sum(k*v for k,v in hl.items())/M:.2f}, naive ceiling={naive:.0f}, record member: {kind(top)}; "
          f"kinds of the top 12: " + ', '.join(sorted(set(kind(d) for d in r['TOP'][:12]))))
    zl = r['lines'][-1]
    cs = q ** (n - cut[zl][2])
    print(f"   line = first {cut[zl][1]} irreducibles (cells of {cs} members)")
    print("   target R | successes | random: members a success | model at the line | cover first: first, half | odd rows left: first, half | "
          "gain of parity at half | optimum cell: rows worse than the best, share of members in cells at least as good")
    for (R, S) in r['targets']:
        J = r['JOINT'][(R, zl)]
        bk = {}; bo = {}
        for k, o, h, s in J:
            a = bk.setdefault(k, [0, 0]); a[0] += h; a[1] += s
            a = bo.setdefault(o, [0, 0]); a[0] += h; a[1] += s
        cover = [(k, v[0], v[1]) for k, v in sorted(bk.items())]
        odd = [(o, v[0], v[1]) for o, v in sorted(bo.items())]
        full = len(cut) - 1
        tot_irr = sum(k * h for k, h, _ in r['HK'][(R, full)])
        pz = tot_irr / sum(k * h for k, h, _ in cover)
        kmin = cover[0][0]
        kbest = min(k for k, h, s in cover if s > 0)
        share = sum(h for k, h, s in cover if k <= kbest) / M
        cf, ch = first_success(cover), to_fraction(cover, .5)
        of, oh = first_success(odd), to_fraction(odd, .5)
        print(f"   {R:5d} | {S:6d} | {M/S:12,.0f} | {model(cover, pz):9.3g} | {cf:12,.0f} {ch:12,.0f} | {of:10,.1f} {oh:10,.1f} | {ch/oh:8.1f} | {kbest - kmin:3d} {100*share:8.3f}%")
    fam = [(nm, sz, h) for nm, sz, h in r.get('FAM', []) if h is not None and nm.startswith('trans')]
    for nm, sz, h in fam:
        cells = [f"{R}: {sum(v for k, v in h.items() if k >= R)} of {int(sz)} (all: {S}, cube-or-q-th root {S ** (1 / r['p'] if 'p' in r else 1):.1f})" for R, S in r['targets']]
        print(f"   {nm}: record {max(h)}; successes " + '; '.join(cells))


if __name__ == '__main__':
    for path in sys.argv[1:]:
        block(path)

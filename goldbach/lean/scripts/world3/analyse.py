#!/usr/bin/env python3
"""Tables from the output of w3 (Goldbach in F_q[t], exact enumeration).

usage: analyse.py OUT.txt [OUT.txt ...]

For each run: the record, the count of successes at each target against the models of independent rows, the
members examined before the first success and before half of the successes in several orders, the table
"optimum at each depth against the scan of the best cells", and the top members.
"""
import sys, math, re


def parse(path):
    r = {'HK': {}, 'HO': {}, 'LINE': {}, 'JOINT': {}, 'TOP': []}
    for ln in open(path):
        w = ln.split()
        if not w:
            continue
        if w[0] == '#':
            for tok in w[1:]:
                if '=' in tok:
                    k, v = tok.split('=')
                    if v.isdigit():
                        r[k] = int(v)
            r['musq'] = int(re.search(r'mu a square: (\d)', ln).group(1))
            r['p'] = 3 if r['q'] == 9 else r['q']
        elif w[0] == 'IRRED':
            r['irred'] = [int(t.split(':')[1]) for t in w[1:]]
        elif w[0] == 'CUTOFFS':
            r['cut'] = [tuple(int(x) for x in t.split(':')) for t in w[1:] if t[0].isdigit()]
        elif w[0] == 'CHECK':
            r['nirr'] = int(w[1].split('=')[1])
        elif w[0] == 'ROWS':
            r['nrow'] = int(w[1])
            r['exhaust'] = int(w[-1])
        elif w[0] == 'HISTL':
            r['histL'] = {int(t.split(':')[0]): int(t.split(':')[1]) for t in w[2:]}
        elif w[0] == 'TARGETS':
            r['targets'] = [tuple(int(x) for x in t.split(':')) for t in w[1:]]
        elif w[0] == 'LINES':
            r['lines'] = [int(t) for t in w[1:]]
        elif w[0] == 'TOP':
            d = dict(t.split('=') for t in w[1:])
            r['TOP'].append(d)
        elif w[0] in ('HK', 'HO'):
            t = int(w[1].split('=')[1]); z = int(w[2].split('=')[1])
            r[w[0]][(t, z)] = [tuple(int(x) for x in tok.split(':')) for tok in w[3:]]
        elif w[0] == 'LINE':
            t = int(w[1].split('=')[1]); zl = int(w[2].split('=')[1]); k = int(w[3].split('=')[1])
            mem = int(w[4].split('=')[1]); i = w.index('min'); j = w.index('mean')
            r['LINE'].setdefault((t, zl), {})[k] = (mem, [int(x) for x in w[i + 1:j]], [float(x) for x in w[j + 1:]])
        elif w[0] == 'JOINT':
            t = int(w[1].split('=')[1]); zl = int(w[2].split('=')[1])
            r['JOINT'][(t, zl)] = [tuple(int(x) for x in tok.split(':')) for tok in w[4:]]
        elif w[0] == 'FAMILY':
            name = w[1]; size = float(w[2].split('=')[1])
            h = {int(t.split(':')[0]): int(t.split(':')[1]) for t in w[4:]} if len(w) > 3 and w[3] == 'HISTL' else None
            r.setdefault('FAM', []).append((name, size, h))
        elif w[0] == 'TIME':
            r['time'] = ln.strip()
    return r


def first_success(levels):
    """levels: list of (key, members, successes) in the order examined; random order inside a level.
    Expected number of members examined up to and including the first success."""
    seen = 0.0
    for _, h, s in levels:
        if s == 0:
            seen += h
        else:
            return seen + (h + 1.0) / (s + 1.0)
    return float('nan')


def to_fraction(levels, frac):
    """Expected members examined until the fraction frac of all the successes has been found."""
    tot = sum(s for _, _, s in levels)
    need = frac * tot
    seen = 0.0; got = 0.0
    for _, h, s in levels:
        if got + s >= need - 1e-12 and s > 0:
            j = need - got
            return seen + j * (h + 1.0) / (s + 1.0)
        seen += h; got += s
    return float('nan')


def model(levels, p):
    return sum(h * (1.0 - p) ** k for k, h, _ in levels)


def report(path):
    r = parse(path)
    q, n, M = r['q'], r['n'], r['members']
    cut = r['cut']
    print('=' * 110)
    print(f"q={q} n={n} mu={r['mu']} ({'square' if r['musq'] else 'NON-square'} leading coefficient)  members {M:,}  "
          f"irreducible of degree n: {r['nirr']:,}  rows used: {r['nrow']}  exhausted: {r['exhaust']}")
    print('cutoffs (index: first r irreducibles, total degree): ' + ', '.join(f"{z}:{rk}:{td}" for z, rk, td in cut))
    hl = r['histL']; Lmax = max(hl); cum = 0
    deg_of_row = []
    for d, c in enumerate(r['irred'], start=1):
        deg_of_row += [d] * c
    p0 = r['nirr'] / M
    naive = math.log(M) / -math.log(1 - p0)
    meanL = sum(k * v for k, v in hl.items()) / M
    print(f"record: L_max = {Lmax} (degree of the first success {deg_of_row[Lmax] if Lmax < len(deg_of_row) else '?'}), "
          f"attained by {hl[Lmax]} members; mean L = {meanL:.2f}; 1/p0 = {1/p0:.2f}; "
          f"naive ceiling ln(members)/-ln(1-p0) = {naive:.0f}; ratio {Lmax/naive:.2f}")
    # largest D: all rows of degree < D fail
    below = 0; best_full = 0
    for d, c in enumerate(r['irred'], start=1):
        below += c
        if Lmax >= below:
            best_full = d
    cnt_full = sum(v for k, v in hl.items() if k >= sum(r['irred'][:best_full]))
    print(f"largest D with every row of degree < D failing: D = {best_full + 1} ({cnt_full} members)")
    for (R, S) in r['targets']:
        print('-' * 110)
        print(f"target: the first {R} rows fail; successes S = {S}; random order: {M / S:,.0f} members a success")
        hk = {z: r['HK'][(R, z)] for z in range(-1, len(cut))}
        ho = {z: r['HO'][(R, z)] for z in range(-1, len(cut))}
        full = len(cut) - 1
        tot_irr = sum(k * h for k, h, _ in hk[full])
        print("  depth z | rows left: mean, min | chance p_z | model successes (indep. rows) | cover order: first success, half |"
              " odd rows left: mean | chance | model | parity order: first, half")
        for z in range(-1, len(cut)):
            lv = hk[z]; lo = ho[z]
            mk = sum(k * h for k, h, _ in lv) / M; mo = sum(k * h for k, h, _ in lo) / M
            pz = tot_irr / max(1, sum(k * h for k, h, _ in lv)); po = tot_irr / max(1, sum(k * h for k, h, _ in lo))
            name = 'none' if z < 0 else f"{cut[z][1]}"
            print(f"  {name:>7} | {mk:8.2f} {lv[0][0]:4d} | {pz:.4f} | {model(lv, pz):12.3g} | {first_success(lv):14,.1f} {to_fraction(lv, 0.5):14,.1f} |"
                  f" {mo:8.2f} | {po:.4f} | {model(lo, po):12.3g} | {first_success(lo):14,.1f} {to_fraction(lo, 0.5):14,.1f}")
        for zl in r['lines']:
            L = r['LINE'][(R, zl)]; ks = sorted(L)
            kmin = ks[0]; cellsize = q ** (n - cut[zl][2]) if n >= cut[zl][2] else 0
            print(f"  line = first {cut[zl][1]} irreducibles (total degree {cut[zl][2]}, cells of {cellsize} members); "
                  f"best cells: {kmin} rows left, {L[kmin][0]} members")
            print("    depth | OPT | scan of the best cells | mean there | design value of the best cell holding an optimum | members at least that good")
            for z in range(zl, len(cut)):
                opt = min(L[k][1][z] for k in ks)
                hold = min(k for k in ks if L[k][1][z] == opt)
                atleast = sum(L[k][0] for k in ks if k <= hold)
                print(f"    {cut[z][1]:5d} | {opt:3d} | {L[kmin][1][z]:3d} | {L[kmin][2][z]:7.2f} | {hold:3d} | {atleast:,}")
            J = r['JOINT'][(R, zl)]
            # orders at the line: cover first (k), cover then parity (k, o), parity of the rows left (o)
            bykey = {}
            for k, o, h, s in J:
                bykey.setdefault(k, [0, 0]); bykey[k][0] += h; bykey[k][1] += s
            cover = [(k, v[0], v[1]) for k, v in sorted(bykey.items())]
            both = [((k, o), h, s) for k, o, h, s in sorted(J)]
            byo = {}
            for k, o, h, s in J:
                byo.setdefault(o, [0, 0]); byo[o][0] += h; byo[o][1] += s
            odd = [(o, v[0], v[1]) for o, v in sorted(byo.items())]
            print(f"    members examined to the first success / to half: cover first {first_success(cover):,.1f} / {to_fraction(cover, .5):,.1f};"
                  f" odd rows left {first_success(odd):,.1f} / {to_fraction(odd, .5):,.1f};"
                  f" cover then parity {first_success(both):,.1f} / {to_fraction(both, .5):,.1f}")
    if r.get('FAM'):
        print('-' * 110)
        print('families (size; then, at each target: successes in the family | expected at the rate of all members | (successes of all)^(1/order of the group) for the symmetric ones)')
        order = {'trans1': r['p'] if 'p' in r else None}
        for name, size, h in r['FAM']:
            if h is None:
                print(f"  {name}: size {size:.0f}, not enumerated"); continue
            cells = []
            for (R, S) in r['targets']:
                sf = sum(v for k, v in h.items() if k >= R)
                cells.append(f"{R}: {sf} | {S * size / M:.3g}")
            print(f"  {name:12s} size {int(size):8d}  record in family {max(h)}  " + ';  '.join(cells))
    print('-' * 110)
    print('top members (L, degree of first success, N\' = 0, values at the points of F_q, odd-squarefree rows among the first L, rows left by depth, odd rows left by depth):')
    for d in r['TOP'][:12]:
        print(f"  L={d['L']} D={d['D']} insep={d['insep']} M={d['M']} values={d['values']} dM={d.get('dM','?')} trans={d.get('trans','?')} scal={d.get('scal','?')} odd={d['odd']} k={d['k']} o={d['o']}")
    if 'time' in r:
        print(r['time'])


if __name__ == '__main__':
    for path in sys.argv[1:]:
        report(path)

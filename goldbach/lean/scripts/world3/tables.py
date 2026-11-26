#!/usr/bin/env python3
"""Markdown tables for the README, from the outputs of w3 (directory RUNS) and of symfam.py (directory SYM).

usage: tables.py RUNS SYM
"""
import sys, os, glob, re, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyse import parse, first_success, to_fraction, model
from summary import kind

runs_dir, sym_dir = sys.argv[1], sys.argv[2]


def key(path):
    m = re.search(r'q(\d+)n(\d+)_mu(\d+)', path)
    return (int(m.group(1)), int(m.group(3)) != 1, int(m.group(2)))


def at_line(r, R):
    """orders at the deepest line of the run for the target R"""
    M = r['members']; cut = r['cut']; zl = r['lines'][-1]
    J = r['JOINT'][(R, zl)]; bk = {}; bo = {}
    for k, o, h, s in J:
        a = bk.setdefault(k, [0, 0]); a[0] += h; a[1] += s
        a = bo.setdefault(o, [0, 0]); a[0] += h; a[1] += s
    cover = [(k, v[0], v[1]) for k, v in sorted(bk.items())]
    odd = [(o, v[0], v[1]) for o, v in sorted(bo.items())]
    tot_irr = sum(k * h for k, h, _ in r['HK'][(R, len(cut) - 1)])
    pz = tot_irr / sum(k * h for k, h, _ in cover)
    kmin = cover[0][0]; kbest = min(k for k, h, s in cover if s > 0)
    share = sum(h for k, h, s in cover if k <= kbest) / M
    return dict(model=model(cover, pz), worse=kbest - kmin, share=share, cover=cover, odd=odd,
                cells=r['q'] ** (r['n'] - cut[zl][2]), line=cut[zl][1])


runs = []
for path in sorted(glob.glob(os.path.join(runs_dir, '*.txt')), key=key):
    if 'TIME' not in open(path).read():
        continue
    runs.append((path, parse(path)))

print('### Records\n')
print('| q | n | leading coefficient | members | record L | D | members with that D | members expected at the record by the cell model | the record member | its cell: rows more than the best cell | members in cells at least as good | reached by cover first after | by the parity order after |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
stats = []
for path, r in runs:
    q, n, M = r['q'], r['n'], r['members']; hl = r['histL']; Lmax = max(hl)
    below = 0; D = 1
    for d, c in enumerate(r['irred'], start=1):
        below += c
        if Lmax >= below: D = d + 1
    nD = sum(v for k, v in hl.items() if k >= sum(r['irred'][:D - 1]))
    R, S = r['targets'][-1]
    a = at_line(r, R)
    cf = first_success(a['cover']) / M; of = first_success(a['odd']) / M
    kd = kind(r['TOP'][0])
    stats.append(dict(model=a['model'], worse=a['worse'], share=a['share'], cf=cf, of=of, kind=kd))
    print(f"| {q} | {n} | {'1' if r['mu'] == 1 else 'non-square'} | {M:,} | {Lmax} | {D} | {nD:,} | {a['model']:.2g} | {kd} | {a['worse']} | {100 * a['share']:.2g}% | {100 * cf:.2g}% | {100 * of:.2g}% |")
print()
print(f"{len(stats)} instances. Record member generic in {sum(1 for s in stats if s['kind'] == 'generic')}. "
      f"Cell model at the record between 0.2 and 10 in {sum(1 for s in stats if 0.2 <= s['model'] <= 10)}. "
      f"Rows more than the best cell: median {statistics.median(s['worse'] for s in stats)}, range {min(s['worse'] for s in stats)} to {max(s['worse'] for s in stats)}. "
      f"Members in cells at least as good: median {100 * statistics.median(s['share'] for s in stats):.2g}%. "
      f"Cover first reaches the record after a median {100 * statistics.median(s['cf'] for s in stats):.2g}% of the members, the parity order after {100 * statistics.median(s['of'] for s in stats):.2g}%.")

print('\n### What cover first finds with a share of the work\n')
print('The largest target of the run (targets: about 10^4, 3000, 1000, 300, 100, 30, 10 and 1 successes) whose first')
print('success comes within the given share of the members, in cover-first order at the line and in the parity order.\n')
print('| q | n | leading coefficient | record L | cover first: 0.01% | 0.1% | 1% | 10% | parity order: 0.01% | 0.1% | 1% |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for path, r in runs:
    M = r['members']
    if M < 10 ** 6:
        continue
    res = {}
    for R, S in r['targets']:
        a = at_line(r, R)
        res[R] = (first_success(a['cover']) / M, first_success(a['odd']) / M)
    def best(ix, w):
        ok = [R for R, v in res.items() if v[ix] <= w]
        return str(max(ok)) if ok else '-'
    print(f"| {r['q']} | {r['n']} | {'1' if r['mu'] == 1 else 'non-square'} | {max(r['histL'])} | " +
          ' | '.join(best(0, w) for w in (1e-4, 1e-3, 1e-2, 1e-1)) + ' | ' + ' | '.join(best(1, w) for w in (1e-4, 1e-3, 1e-2)) + ' |')

print('\n### Targets, cover first against the parity order\n')
for path, r in runs:
    if (r['q'], r['n'], r['mu']) not in ((3, 15, 1), (3, 17, 1), (3, 18, 1), (5, 10, 1), (5, 12, 1), (7, 10, 1), (9, 8, 1), (9, 9, 1)):
        continue
    M = r['members']
    a0 = at_line(r, r['targets'][0][0])
    print(f"q = {r['q']}, n = {r['n']}, monic; line = first {a0['line']} irreducibles, cells of {a0['cells']} members.\n")
    print('| target (rows) | successes | cell model | members before half of the successes: cover first | parity order | ratio | members before the first success: cover first | parity order |')
    print('|---|---|---|---|---|---|---|---|')
    for R, S in r['targets']:
        a = at_line(r, R)
        ch, oh = to_fraction(a['cover'], .5), to_fraction(a['odd'], .5)
        print(f"| {R} | {S:,} | {a['model']:,.3g} | {ch:,.0f} | {oh:,.0f} | {ch / oh:,.1f} | {first_success(a['cover']):,.0f} | {first_success(a['odd']):,.0f} |")
    print()

print('### The optimum at each depth against the best member of the best cells (record target)\n')
for path, r in runs:
    if (r['q'], r['n'], r['mu']) not in ((3, 15, 1), (3, 16, 1), (3, 17, 1), (3, 18, 1), (5, 12, 1), (7, 10, 1), (9, 9, 1)):
        continue
    R, S = r['targets'][-1]; cut = r['cut']; zl = r['lines'][-1]
    L = r['LINE'][(R, zl)]; ks = sorted(L); kmin = ks[0]
    cells = r['q'] ** (r['n'] - cut[zl][2])
    print(f"q = {r['q']}, n = {r['n']}, monic, the first {R} rows; line = first {cut[zl][1]} irreducibles (cells of {cells} members); "
          f"the best cells have {kmin} rows left and {L[kmin][0]} members.\n")
    print('| depth (irreducibles sieved) | optimum over all members | best member of the best cells | mean there | rows left at the line of the best cell holding an optimum | members in cells at least that good |')
    print('|---|---|---|---|---|---|')
    for z in range(zl, len(cut)):
        opt = min(L[k][1][z] for k in ks)
        hold = min(k for k in ks if L[k][1][z] == opt)
        atleast = sum(L[k][0] for k in ks if k <= hold)
        print(f"| {cut[z][1]} | {opt} | {L[kmin][1][z]} | {L[kmin][2][z]:.1f} | {hold} | {atleast:,} |")
    print()

print('### The translation-invariant family\n')
print('F_d = members of the family with every row of degree at most d failing; G_d = members of all with the same,')
print('from the cell model. The law is F_d ≈ G_d^(1/p).\n')
print('| q | n | members of the family | all members | d | rows of degree ≤ d | F_d | G_d | G_d^(1/p) |')
print('|---|---|---|---|---|---|---|---|---|')
def skey(p):
    m = re.search(r'q(\d+)n(\d+)', p); return (int(m.group(1)), int(m.group(2)))
fam_rows = []
for path in sorted(glob.glob(os.path.join(sym_dir, 'q*.txt')), key=skey):
    s = open(path).read()
    m1 = re.search(r'q=(\d+) n=(\d+): .* family of (\d+) members', s)
    m2 = re.search(r'family best: L=(\d+) \(D=([>\d]+),', s)
    m3 = re.search(r'expected: (\S+), (\S+), (\S+)', s)
    m4 = re.search(r"best level L >= \d+: (\S+)", s)
    if not (m1 and m2 and m3):
        continue
    q, n, fam = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
    fam_rows.append((q, n, fam, m2.group(1), m2.group(2), m3.groups(), m4.group(1) if m4 else 'beyond the rows used'))
    for d, rws, F, G, root in re.findall(r'd=(\d+): rows (\d+) \| family (\d+) of \d+ \| all (\S+) \| root (\S+)', s):
        if int(F) > 0 or float(root) > 0.005:
            if float(G) < 0.3 * q ** n:
                print(f"| {q} | {n} | {fam:,} | {q ** n:.2g} | {d} | {int(rws):,} | {int(F):,} | {float(G):.3g} | {float(root):.3g} |")
print()
print("| q | n | best L in the family | D | level of the best of all members (cell model: 10, 1, 0.1 members expected) | members of all expected at the family's best L |")
print('|---|---|---|---|---|---|')
for q, n, fam, L, D, lv, ex in fam_rows:
    print(f"| {q} | {n} | {L} | {D} | {lv[0]} {lv[1]} {lv[2]} | {ex} |")

#!/usr/bin/env python3
"""Aggregate analysis of index.jsonl. Usage: python3 -I analyze.py <out_dir>"""
import json, sys, os, collections, sys
OUT = sys.argv[1]
sys.setrecursionlimit(10000)

recs = {}
with open(os.path.join(OUT, 'index.jsonl')) as f:
    for line in f:
        r = json.loads(line)
        recs[r['module']] = r

mods = set(recs)
def top(m): return m.split('.')[0]
def sub(m):
    p = m.split('.')
    return '.'.join(p[:2]) if len(p) > 1 else p[0]

rep = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    rep.append(s); print(s)

# ---------- totals ----------
P('## TOTALS')
P('modules', len(recs), 'lines', sum(r['lines'] for r in recs.values()), 'bytes', sum(r['bytes'] for r in recs.values()))
kinds = collections.Counter()
for r in recs.values():
    for k, _ in r['decls']:
        kinds[k] += 1
P('declaration kinds', dict(kinds))
P('named Prop-defs (statements-as-defs)', sum(len(r['props']) for r in recs.values()))
fl = collections.Counter()
flmods = collections.defaultdict(list)
for r in recs.values():
    for k, v in r['flags'].items():
        fl[k] += v
        flmods[k].append(r['module'])
P('trust-relevant construct counts (text matches):', dict(fl))
for k in ('sorry', 'axiom', 'native_decide', 'unsafe', 'implemented_by', 'run_cmd', 'elab_macro', 'io_sys', 'opaque'):
    if flmods.get(k):
        P(' ', k, 'in', len(flmods[k]), 'files; first:', flmods[k][:6])

# ---------- import graph ----------
ext = collections.Counter()
edges = {}
indeg = collections.Counter()
for m, r in recs.items():
    es = []
    for i in r['imports']:
        if i in mods:
            es.append(i); indeg[i] += 1
        else:
            ext[i.split('.')[0]] += 1
    edges[m] = es
P('\n## EXTERNAL IMPORT ROOTS (non-archive)', dict(ext.most_common(10)))
P('files that import Mathlib directly:', sum(1 for r in recs.values() if 'Mathlib' in r['imports']))
P('total internal import edges', sum(len(v) for v in edges.values()))

# reachability from Main
roots = [m for m in ('Main', 'Statements') if m in mods]
seen = set(); stack = list(roots)
while stack:
    m = stack.pop()
    if m in seen: continue
    seen.add(m)
    stack.extend(edges.get(m, []))
P('\n## REACHABILITY from Main+Statements:', len(seen), 'of', len(mods), 'modules (', round(100 * len(seen) / len(mods), 2), '%)')
unreach = mods - seen
P('not reachable from Main:', len(unreach))
byd = collections.Counter(sub(m) for m in unreach)
P(' unreachable by area (top 25):', byd.most_common(25))
reach_by = collections.Counter(top(m) for m in seen)
P(' reachable by library:', dict(reach_by))
reach_lines = sum(recs[m]['lines'] for m in seen)
P(' reachable lines:', reach_lines)

# depth (longest path from leaves) via memoized DFS iterative
depth = {}
def compute_depth(start):
    stack = [(start, 0)]
    while stack:
        m, st = stack.pop()
        if m in depth and st == 0: continue
        if st == 0:
            stack.append((m, 1))
            for c in edges.get(m, []):
                if c not in depth:
                    stack.append((c, 0))
        else:
            depth[m] = 1 + max((depth[c] for c in edges.get(m, []) if c in depth), default=0)
for m in mods:
    if m not in depth:
        compute_depth(m)
maxd = max(depth.values())
P('\n## LAYERING: longest import chain length =', maxd)
layer = collections.Counter(depth[m] // 10 * 10 for m in seen)
P(' reachable modules by depth bucket:', sorted(layer.items()))
# critical path from Main
def critical_path(m):
    path = [m]
    while edges.get(m):
        m = max(edges[m], key=lambda c: depth.get(c, 0))
        path.append(m)
    return path
cp = critical_path('Main')
P(' critical path from Main (first 15 / last 10 of %d):' % len(cp))
for x in cp[:15]: P('   ', x, depth[x])
P('   ...')
for x in cp[-10:]: P('   ', x, depth[x])

# cross library edge matrix (top-level libs)
mat = collections.Counter()
for m, es in edges.items():
    for c in es:
        if top(m) != top(c):
            mat[(top(m), top(c))] += 1
P('\n## CROSS-LIBRARY IMPORT EDGES (importer -> imported):')
for (a, b), n in mat.most_common(40):
    P('  %s -> %s : %d' % (a, b, n))

# hubs
P('\n## TOP HUBS (most imported modules)')
for m, n in indeg.most_common(40):
    P('  %6d  %s   (%d lines)' % (n, m, recs[m]['lines']))

# per-area table
P('\n## PER SECOND-LEVEL AREA: files / Mlines / decls / props / has-moddoc%')
area = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for m, r in recs.items():
    a = area[sub(m)]
    a[0] += 1; a[1] += r['lines']; a[2] += r['ndecl']; a[3] += len(r['props']); a[4] += 1 if r['moddoc'] else 0
rows = sorted(area.items(), key=lambda kv: -kv[1][1])
for k, v in rows[:90]:
    P('  %-62s %7d %8.2f %8d %6d %5.1f%%' % (k, v[0], v[1] / 1e6, v[2], v[3], 100 * v[4] / v[0]))

json.dump({'depth': depth, 'indeg': indeg}, open(os.path.join(OUT, 'graph_stats.json'), 'w'))
json.dump(sorted(seen), open(os.path.join(OUT, 'reachable.json'), 'w'))
open(os.path.join(OUT, 'report_structure.txt'), 'w').write('\n'.join(rep))

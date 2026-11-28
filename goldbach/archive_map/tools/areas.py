#!/usr/bin/env python3
"""Per-area catalogue: files, Mlines, #named statements, hub modules and representative statement names.
Usage: python3 -I areas.py <out_dir> [minfiles] [depth]"""
import json, sys, os, collections, re
OUT = sys.argv[1]
MINF = int(sys.argv[2]) if len(sys.argv) > 2 else 15
DEPTH = int(sys.argv[3]) if len(sys.argv) > 3 else 2
gs = json.load(open(os.path.join(OUT, 'graph_stats.json')))
indeg = gs['indeg']
area = collections.defaultdict(lambda: {'files': 0, 'lines': 0, 'props': [], 'hubs': [], 'decls': 0})
for line in open(os.path.join(OUT, 'index.jsonl')):
    r = json.loads(line)
    key = '.'.join(r['module'].split('.')[:DEPTH])
    a = area[key]
    a['files'] += 1; a['lines'] += r['lines']; a['decls'] += r['ndecl']
    for n, _ in r['props']:
        a['props'].append(n.split('.')[-1])
    a['hubs'].append((indeg.get(r['module'], 0), r['module'].split('.')[-1]))
rows = sorted(area.items(), key=lambda kv: -kv[1]['lines'])
for k, a in rows:
    if a['files'] < MINF:
        continue
    ps = sorted(set(a['props']), key=lambda s: (len(s), s))
    # prefer mid-length descriptive names
    cand = [p for p in ps if 10 <= len(p) <= 34][:9] or ps[:9]
    hubs = [h for _, h in sorted(a['hubs'], reverse=True)[:4]]
    print('## %s | %d files | %.2fM lines | %d decls | %d statements' % (k, a['files'], a['lines'] / 1e6, a['decls'], len(a['props'])))
    print('   hubs:', ', '.join(h[:38] for h in hubs))
    print('   stmts:', ', '.join(cand))

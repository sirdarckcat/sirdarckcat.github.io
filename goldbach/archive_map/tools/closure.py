#!/usr/bin/env python3
"""Transitive import closure of modules. Usage: python3 -I closure.py <out_dir> <module> [<module> ...]
Prints closure size, lines, per-library breakdown and estimated build time at 9.6 s/file (1 core)."""
import json, sys, os, collections
OUT = sys.argv[1]
targets = sys.argv[2:]
imports = {}; lines = {}
for line in open(os.path.join(OUT, 'index.jsonl')):
    r = json.loads(line)
    imports[r['module']] = r['imports']; lines[r['module']] = r['lines']
def closure(t):
    seen = set(); st = [t]
    while st:
        m = st.pop()
        if m in seen or m not in imports:
            continue
        seen.add(m)
        st.extend(imports[m])
    return seen
for t in targets:
    if t not in imports:
        print('!! not an archive module:', t); continue
    c = closure(t)
    by = collections.Counter(m.split('.')[0] + '.' + (m.split('.')[1] if len(m.split('.')) > 1 else '') for m in c)
    print('== %s' % t)
    print('   closure: %d files, %.2fM lines, ~%.1f core-hours at 9.6 s/file' % (len(c), sum(lines[m] for m in c) / 1e6, len(c) * 9.6 / 3600))
    print('   by area:', dict(by.most_common(6)))
    json.dump(sorted(c), open(os.path.join(OUT, 'closure_' + t.split('.')[-1][:60] + '.json'), 'w'))

#!/usr/bin/env python3
"""Query tool. python3 -I q.py <out_dir> <mode> <regex> [limit]
modes: props  (search named Prop defs: name or statement text)
       decls  (search declaration names)
       mods   (search module names)
       imps   (modules importing a module matching regex)
"""
import json, sys, os, re
OUT, mode, pat = sys.argv[1], sys.argv[2], sys.argv[3]
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 40
rx = re.compile(pat, re.I)
n = 0
for line in open(os.path.join(OUT, 'index.jsonl')):
    r = json.loads(line)
    if mode == 'mods':
        if rx.search(r['module']):
            print(r['module'], r['lines']); n += 1
    elif mode == 'decls':
        for k, name in r['decls']:
            if rx.search(name):
                print(f"{k:9s} {name}   [{r['module']}]"); n += 1
                if n >= limit: break
    elif mode == 'props':
        for name, hdr in r['props']:
            if rx.search(name) or rx.search(hdr):
                print(f"--- {name}   [{r['module']}]\n{hdr[:700]}"); n += 1
                if n >= limit: break
    elif mode == 'imps':
        for i in r['imports']:
            if rx.search(i):
                print(r['module'], '<-', i); n += 1
                break
    if n >= limit:
        break
print('# matches printed:', n)

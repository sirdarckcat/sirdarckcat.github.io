#!/usr/bin/env python3
"""Explicit-reference graph tools for the archive (text only; nothing is executed).
  python3 -I keygraph.py <src> <out> resolve <regex> [limit]
  python3 -I keygraph.py <src> <out> show <fullname> [maxlines]
  python3 -I keygraph.py <src> <out> build <spec.json> <graph.json>
Reference resolution is approximate (see cone.py): an edge A->B means a token in A's source text
resolved to declaration B. Implicit uses (instances, simp sets, macros) are not followed."""
import os, re, sys, json, time, pickle, collections
from multiprocessing import Pool

SRC, OUT, CMD = sys.argv[1], sys.argv[2], sys.argv[3]
ARGS = sys.argv[4:]

COMMENT = re.compile(r'/-.*?-/|--[^\n]*', re.S)
def code_only(t):
    return COMMENT.sub(' ', t)

DECL = re.compile(
    r'^(?:@\[[^\]\n]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*'
    r'(theorem|lemma|def|abbrev|structure|class|inductive|instance|axiom|opaque)\s+([^\s:\(\{\[⦃]+)')
NS = re.compile(r'^namespace\s+(\S+)')
SECTION = re.compile(r'^(?:noncomputable\s+)?section\b|^mutual\b')
END = re.compile(r'^end\b')
OPEN = re.compile(r'^open\s+(.*)')
VAR = re.compile(r'^variable\b')
IDENT = re.compile(r"[A-Za-z_\u00C0-\u024F\u0370-\u03FF\u1D00-\u1DBF\u1E00-\u1EFF][A-Za-z0-9_'!?\u00C0-\u024F\u0370-\u03FF\u2080-\u209F\u1D00-\u1DBF.]*")

def module_of(path):
    return os.path.relpath(path, SRC)[:-5].replace(os.sep, '.')

def peel_doc(lines):
    """Split off a docstring / attribute block that directly precedes the next declaration."""
    j = len(lines)
    while j > 0 and lines[j - 1].lstrip().startswith('@['):
        j -= 1
    k = j
    if k > 0 and lines[k - 1].rstrip().endswith('-/'):
        m = k - 1
        while m >= 0 and not lines[m].lstrip().startswith('/-'):
            if m < k - 1 and '-/' in lines[m]:
                m = -1
                break
            m -= 1
        if m >= 0:
            return lines[:m], lines[m:]
    return lines[:j], lines[j:]

def segments(path):
    try:
        lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    except Exception:
        return [], [], ''
    frames, opens, vartext, segs, cur = [], [], [], [], None
    for ln in lines:
        m = DECL.match(ln)
        if m:
            carry = []
            if cur:
                cur[2], carry = peel_doc(cur[2])
                segs.append(cur)
            name = m.group(2)
            ns = tuple(c for f in frames for c in f)
            full = name[7:] if name.startswith('_root_.') else '.'.join(list(ns) + [name])
            cur = [full, ns, carry + [ln]]
            continue
        if not ln.startswith((' ', '\t')):
            mm = NS.match(ln)
            if mm:
                if cur: segs.append(cur); cur = None
                frames.append(tuple(mm.group(1).split('.'))); continue
            if SECTION.match(ln):
                if cur: segs.append(cur); cur = None
                frames.append(()); continue
            if END.match(ln):
                if cur: segs.append(cur); cur = None
                if frames: frames.pop()
                continue
            mo = OPEN.match(ln)
            if mo:
                for t in re.split(r'[\s()]+', mo.group(1)):
                    if t and t not in ('scoped', 'in', 'hiding', 'renaming') and not t.startswith('-'):
                        opens.append(t)
                continue
            if VAR.match(ln):
                vartext.append(ln); continue
        if cur is not None:
            cur[2].append(ln)
    if cur: segs.append(cur)
    return [(f, ns, '\n'.join(t)) for f, ns, t in segs], opens, '\n'.join(vartext)

def pass1(path):
    segs, _, _ = segments(path)
    return module_of(path), [f for f, _, _ in segs]

def load_decls():
    pk = os.path.join(OUT, 'decls.pkl')
    if os.path.exists(pk):
        return pickle.load(open(pk, 'rb'))
    files = []
    for r, _, fs in os.walk(SRC):
        for f in fs:
            if f.endswith('.lean'):
                files.append(os.path.join(r, f))
    files.sort()
    decl2mod = {}
    with Pool(4) as pool:
        for mod, names in pool.imap(pass1, files, chunksize=64):
            for n in names:
                decl2mod.setdefault(n, mod)
    mod2path = {module_of(p): p for p in files}
    pickle.dump((decl2mod, mod2path), open(pk, 'wb'))
    return decl2mod, mod2path

decl2mod, mod2path = load_decls()
lastcomp = {n.rsplit('.', 1)[-1] for n in decl2mod}
cache = {}

def mod_deps(mod):
    if mod in cache: return cache[mod]
    segs, opens, vartext = segments(mod2path[mod])
    vtoks = set(IDENT.findall(vartext)) if vartext else set()
    out = {}
    for full, ns, text in segs:
        toks = set(IDENT.findall(code_only(text))) | vtoks
        deps = set()
        for t in toks:
            last = t.rsplit('.', 1)[-1]
            if last not in lastcomp and t not in lastcomp:
                if '.' not in t: continue
            cands = [t] + ['.'.join(ns[:k]) + '.' + t for k in range(len(ns), 0, -1)] + [o + '.' + t for o in opens]
            if t.startswith('_root_.'): cands.append(t[7:])
            hit = next((c for c in cands if c in decl2mod), None)
            if hit is None and '.' in t:
                parts = t.split('.')
                for drop in (1, 2):
                    if len(parts) - drop >= 1:
                        tt = '.'.join(parts[:-drop])
                        hit = next((c for c in [tt] + ['.'.join(ns[:k]) + '.' + tt for k in range(len(ns), 0, -1)] + [o + '.' + tt for o in opens] if c in decl2mod), None)
                    if hit: break
            if hit and hit != full:
                # drop root-level short names (local variables such as s1, R, one, inj, key ...)
                if '.' not in hit and not (len(hit) >= 6 and (any(c.isupper() for c in hit[1:]) or '_' in hit)):
                    continue
                deps.add(hit)
        out[full] = (deps, text)
    cache[mod] = out
    return out

def resolve_decl(d):
    if d in decl2mod: return d
    cands = sorted([x for x in decl2mod if x.endswith('.' + d)], key=len)
    return cands[0] if cands else None

def cmd_resolve():
    rx = re.compile(ARGS[0]); lim = int(ARGS[1]) if len(ARGS) > 1 else 30
    n = 0
    for name, mod in decl2mod.items():
        if rx.search(name):
            print('%s   [%s]' % (name, mod)); n += 1
            if n >= lim: break
    print('# printed', n)

def cmd_show():
    name = ARGS[0]; mx = int(ARGS[1]) if len(ARGS) > 1 else 14
    if name not in decl2mod:
        print('not found'); return
    mod = decl2mod[name]
    deps, text = mod_deps(mod)[name]
    print('NAME  ', name); print('MODULE', mod)
    print('--- source (first %d lines)' % mx)
    for l in text.split('\n')[:mx]: print('   ', l[:260])
    print('--- direct references (%d):' % len(deps))
    for d in sorted(deps): print('   %s   [%s]' % (d, decl2mod[d].split('.')[-1][:60]))

def cmd_build():
    spec = json.load(open(ARGS[0])); outp = ARGS[1]
    t0 = time.time()
    keys = {}; alias = {}
    bad = False
    for n in spec['nodes']:
        d = n['decl']
        r = resolve_decl(d)
        if r is None:
            print('!! unresolved', n['id'], d); bad = True; continue
        keys[n['id']] = r; alias[r] = n['id']
        for a in n.get('also', []):
            ra = resolve_decl(a)
            if ra is None: print('!! unresolved also', n['id'], a); bad = True; continue
            alias[ra] = n['id']
    if bad: return
    info = {}
    for i, d in keys.items():
        deps, text = mod_deps(decl2mod[d])[d]
        kind = (DECL.match(text.split('\n')[0]) or [None, '?'])[1] if DECL.match(text.split('\n')[0]) else '?'
        info[i] = {'decl': d, 'module': decl2mod[d], 'kind': kind, 'source': text[:1600], 'nrefs': len(deps)}
    # explicit-reference graph from all keys (lazy BFS over modules)
    graph = {}
    stack = list(alias.keys())
    while stack:
        d = stack.pop()
        if d in graph: continue
        deps = mod_deps(decl2mod[d])[d][0]
        graph[d] = deps
        for x in deps:
            if x not in graph: stack.append(x)
        if len(graph) % 100000 == 0:
            print('  graph nodes', len(graph), 'elapsed %.0fs' % (time.time() - t0), flush=True)
    print('graph: %d decls (%.0fs)' % (len(graph), time.time() - t0), flush=True)
    key_decls = set(alias.keys()); d2id = dict(alias)
    starts = collections.defaultdict(list)
    for d, i in alias.items(): starts[i].append(d)
    reach = {}; paths = {}; stats = {}
    for kid, kd in keys.items():
        parent = {d: None for d in starts[kid]}; q = collections.deque(starts[kid]); seen_keys = set()
        while q:
            x = q.popleft()
            for y in graph.get(x, ()):
                if y not in parent:
                    parent[y] = x; q.append(y)
        reach[kid] = {d2id[d] for d in parent if d in key_decls and d2id[d] != kid}
        mods = {decl2mod[d] for d in parent if d in decl2mod}
        stats[kid] = {'decls': len(parent), 'modules': len(mods)}
        pp = {}
        for d in parent:
            if d in key_decls and d2id[d] != kid:
                path = []; x = d
                while x is not None:
                    path.append(x); x = parent[x]
                pp[d2id[d]] = path[::-1]
        paths[kid] = pp
    edges = []
    for a in keys:
        for b in reach[a]:
            # transitive reduction among key nodes
            if any((c != a and c != b and c in reach[a] and b in reach[c]) for c in keys):
                continue
            direct = any(db in graph[da] for da in starts[a] for db in starts[b])
            edges.append({'from': a, 'to': b, 'direct': direct, 'path': paths[a][b]})
    json.dump({'info': info, 'stats': stats, 'edges': edges, 'reach': {k: sorted(v) for k, v in reach.items()}}, open(outp, 'w'))
    for e in sorted(edges, key=lambda e: (e['from'], e['to'])):
        print('  %-18s -> %-18s %s hops=%d' % (e['from'], e['to'], 'D' if e['direct'] else 'v', len(e['path']) - 1))
    print('edges after reduction:', len(edges), 'direct:', sum(1 for e in edges if e['direct']), '(%.0fs)' % (time.time() - t0))

def cmd_brief():
    nlines = int(ARGS[0])
    for suffix in ARGS[1:]:
        cands = [n for n in decl2mod if n == suffix or n.endswith('.' + suffix)]
        if not cands:
            print('## %s : NOT FOUND\n' % suffix); continue
        cands.sort(key=lambda n: (n != suffix, len(n)))
        name = cands[0]
        deps, text = mod_deps(decl2mod[name])[name]
        print('## %s   [%s]%s' % (name, decl2mod[name], '  (+%d other matches)' % (len(cands) - 1) if len(cands) > 1 else ''))
        for l in text.split('\n')[:nlines]:
            if l.strip(): print('   ', l[:300])
        print('   refs:', len(deps))
        print()

def cmd_direct():
    spec = json.load(open(ARGS[0])); outp = ARGS[1]
    keys = {}; d2id = {}; starts = collections.defaultdict(list)
    for n in spec['nodes']:
        r = resolve_decl(n['decl'])
        if r is None: print('!! unresolved', n['id'], n['decl']); continue
        keys[n['id']] = r; d2id[r] = n['id']; starts[n['id']].append(r)
        for a in n.get('also', []):
            ra = resolve_decl(a)
            if ra is None: print('!! unresolved also', n['id'], a); continue
            d2id[ra] = n['id']; starts[n['id']].append(ra)
    out = []; seen = set()
    for kid in keys:
        for kd in starts[kid]:
            deps = mod_deps(decl2mod[kd])[kd][0]
            for x in deps:
                if x in d2id and d2id[x] != kid and (kid, d2id[x]) not in seen:
                    seen.add((kid, d2id[x])); out.append({'from': kid, 'to': d2id[x], 'via': [kd, x]})
    json.dump({'direct': out, 'decls': keys}, open(outp, 'w'))
    print('direct edges among key nodes:', len(out))
    for e in sorted(out, key=lambda e: (e['from'], e['to'])): print('  %-16s -> %s' % (e['from'], e['to']))

{'resolve': cmd_resolve, 'show': cmd_show, 'build': cmd_build, 'brief': cmd_brief, 'direct': cmd_direct}[CMD]()

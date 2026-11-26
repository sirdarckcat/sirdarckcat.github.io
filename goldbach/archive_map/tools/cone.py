#!/usr/bin/env python3
"""Approximate NAME-LEVEL dependency cone (lower bound: explicit textual references only;
implicit instances / simp lemmas / macros are NOT followed).
Usage: python3 -I cone.py <src_dir> <out_dir> <root_full_name> [<root_full_name> ...]
Text is parsed only; nothing from the archive is executed."""
import os, re, sys, json, time, collections
from multiprocessing import Pool

SRC, OUT = sys.argv[1], sys.argv[2]
ROOTS = sys.argv[3:]

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

def segments(path):
    """yield (fullname, ns_tuple, text); also returns file-level opens and variable-line text."""
    try:
        lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    except Exception:
        return [], [], ''
    frames = []  # list of tuples of namespace components
    opens = []
    vartext = []
    segs = []
    cur = None  # [fullname, ns_tuple, [lines]]
    for ln in lines:
        s = ln.lstrip() if ln.startswith(' ') is False else ln  # keep indentation semantics: decls start col 0
        m = DECL.match(ln)
        if m:
            if cur: segs.append(cur)
            name = m.group(2)
            ns = tuple(c for f in frames for c in f)
            if name.startswith('_root_.'):
                full = name[7:]
            else:
                full = '.'.join(list(ns) + [name])
            cur = [full, ns, [ln]]
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
                toks = re.split(r'[\s()]+', mo.group(1))
                for t in toks:
                    if t and t not in ('scoped', 'in', 'hiding', 'renaming') and not t.startswith('-'):
                        opens.append(t)
                continue
            if VAR.match(ln):
                vartext.append(ln)
                continue
        if cur is not None:
            cur[2].append(ln)
    if cur: segs.append(cur)
    return [(f, ns, '\n'.join(t)) for f, ns, t in segs], opens, '\n'.join(vartext)

def pass1(path):
    segs, _, _ = segments(path)
    return module_of(path), [f for f, _, _ in segs]

def main():
    t0 = time.time()
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
    print('pass1: %d declaration names in %d files (%.0fs)' % (len(decl2mod), len(files), time.time() - t0), flush=True)
    lastcomp = set()
    for n in decl2mod:
        lastcomp.add(n.rsplit('.', 1)[-1])
    mod2path = {module_of(p): p for p in files}

    cache = {}
    def mod_deps(mod):
        if mod in cache: return cache[mod]
        segs, opens, vartext = segments(mod2path[mod])
        vtoks = set(IDENT.findall(vartext)) if vartext else set()
        out = {}
        for full, ns, text in segs:
            toks = set(IDENT.findall(text)) | vtoks
            deps = set()
            for t in toks:
                last = t.rsplit('.', 1)[-1]
                if last not in lastcomp and t not in lastcomp:
                    # maybe a projection suffix: try prefix
                    if '.' not in t: continue
                cands = [t]
                for k in range(len(ns), 0, -1):
                    cands.append('.'.join(ns[:k]) + '.' + t)
                for o in opens:
                    cands.append(o + '.' + t)
                if t.startswith('_root_.'):
                    cands.append(t[7:])
                hit = None
                for c in cands:
                    if c in decl2mod:
                        hit = c; break
                if hit is None and '.' in t:
                    # drop trailing projection components (up to 2)
                    parts = t.split('.')
                    for drop in (1, 2):
                        if len(parts) - drop >= 1:
                            tt = '.'.join(parts[:-drop])
                            for c in [tt] + ['.'.join(ns[:k]) + '.' + tt for k in range(len(ns), 0, -1)] + [o + '.' + tt for o in opens]:
                                if c in decl2mod:
                                    hit = c; break
                        if hit: break
                if hit and hit != full:
                    deps.add(hit)
            out[full] = deps
        cache[mod] = out
        if len(cache) % 500 == 0:
            print('  parsed modules:', len(cache), 'elapsed %.0fs' % (time.time() - t0), flush=True)
        return out

    visited = set(); frontier = []
    for r in ROOTS:
        if r in decl2mod:
            frontier.append(r)
        else:
            print('!! root not found:', r)
    while frontier:
        d = frontier.pop()
        if d in visited: continue
        visited.add(d)
        deps = mod_deps(decl2mod[d]).get(d, ())
        for x in deps:
            if x not in visited:
                frontier.append(x)
        if len(visited) % 20000 == 0:
            print('  visited decls:', len(visited), 'modules parsed:', len(cache), 'elapsed %.0fs' % (time.time() - t0), flush=True)
    mods = collections.Counter(decl2mod[d] for d in visited)
    print('\nCONE (explicit references only): %d declarations in %d modules (of %d modules; %.1f%%)' % (len(visited), len(mods), len(files), 100 * len(mods) / len(files)))
    byarea = collections.Counter('.'.join(m.split('.')[:2]) for m in mods)
    print('modules by area:', byarea.most_common(25))
    json.dump(sorted(mods), open(os.path.join(OUT, 'cone_modules.json'), 'w'))
    json.dump(sorted(visited), open(os.path.join(OUT, 'cone_decls.json'), 'w'))
    print('done %.0fs' % (time.time() - t0))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Static indexer for the Lean archive. Reads text only; never executes anything from the archive.
Usage: python3 -I index.py <src_dir> <out_dir>
"""
import os, re, sys, json
from multiprocessing import Pool

SRC, OUT = sys.argv[1], sys.argv[2]

DECL = re.compile(
    r'^(?:@\[[^\]\n]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*'
    r'(theorem|lemma|def|abbrev|structure|class|inductive|instance|axiom|opaque)\s+([^\s:\(\{\[⦃]+)?',
    re.M)
MODDOC = re.compile(r'/-!(.*?)-/', re.S)
IMPORT = re.compile(r'^import\s+([^\s]+)', re.M)
NAMESPACE = re.compile(r'^namespace\s+([^\s]+)', re.M)
FLAGS = {
    'sorry': re.compile(r'\bsorry\b'),
    'axiom': re.compile(r'^\s*axiom\b', re.M),
    'native_decide': re.compile(r'native_decide'),
    'unsafe': re.compile(r'\bunsafe\b'),
    'implemented_by': re.compile(r'implemented_by|@\[extern'),
    'run_cmd': re.compile(r'run_cmd|run_elab|run_meta|#eval|initialize\b'),
    'elab_macro': re.compile(r'^\s*(?:elab|macro|syntax|macro_rules|elab_rules|declare_syntax_cat)\b', re.M),
    'set_option': re.compile(r'^\s*set_option\b', re.M),
    'io_sys': re.compile(r'\bIO\.|System\.|IO\.Process|FS\.'),
    'opaque': re.compile(r'^\s*(?:private\s+)?opaque\b', re.M),
}

def module_of(path):
    rel = os.path.relpath(path, SRC)
    return rel[:-5].replace(os.sep, '.')

def parse(path):
    try:
        txt = open(path, 'r', encoding='utf-8', errors='replace').read()
    except Exception as e:
        return {'module': module_of(path), 'error': str(e)}
    mod = module_of(path)
    imports = IMPORT.findall(txt)
    md = MODDOC.search(txt)
    moddoc = md.group(1).strip()[:3000] if md else ''
    decls = []
    props = []
    for m in DECL.finditer(txt):
        kind, name = m.group(1), m.group(2) or ''
        line = txt.count('\n', 0, m.start()) + 1 if False else None
        decls.append((kind, name))
        if kind in ('def', 'abbrev'):
            head = txt[m.end():m.end() + 700]
            cut = head.find(':=')
            if cut < 0:
                cut = len(head)
            hdr = head[:cut]
            if re.search(r':\s*Prop\s*$', hdr.rstrip()) or re.match(r'\s*(?:[\(\{\[][^:]*:[^)\]}]*[\)\]\}]\s*)*:\s*Prop\b', hdr):
                props.append((name, (head[:cut + 600]).strip()[:900]))
    flags = {k: len(v.findall(txt)) for k, v in FLAGS.items()}
    return {
        'module': mod,
        'lines': txt.count('\n') + 1,
        'bytes': len(txt.encode('utf-8', 'replace')),
        'imports': imports,
        'moddoc': moddoc,
        'namespaces': NAMESPACE.findall(txt)[:3],
        'ndecl': len(decls),
        'decls': decls,
        'props': props,
        'flags': {k: v for k, v in flags.items() if v},
    }

def main():
    files = []
    for r, _, fs in os.walk(SRC):
        for f in fs:
            if f.endswith('.lean'):
                files.append(os.path.join(r, f))
    files.sort()
    os.makedirs(OUT, exist_ok=True)
    n = 0
    with Pool(4) as pool, open(os.path.join(OUT, 'index.jsonl'), 'w') as out:
        for rec in pool.imap(parse, files, chunksize=64):
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n += 1
            if n % 20000 == 0:
                print('parsed', n, flush=True)
    print('done', n)

if __name__ == '__main__':
    main()

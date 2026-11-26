#!/usr/bin/env python3
"""Print docstring + statement of named theorems. python3 -I lean_stmt.py <root> Module:name Module:name ..."""
import re, sys, os
root = sys.argv[1]
for spec in sys.argv[2:]:
    mod, name = spec.split(':')
    path = os.path.join(root, mod.replace('.', '/') + '.lean')
    if not os.path.exists(path): print('## %s : NO FILE' % spec); continue
    t = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'(?:^|\n)((?:/--(?:(?!-/).)*-/\s*)?)(?:@\[[^\]]*\]\s*)*(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma|def)\s+(?:\S+\.)?' + re.escape(name) + r'\b(.*?)(?::=|\n\n)', t, re.S)
    if not m: print('## %s : NOT FOUND' % spec); continue
    doc = re.sub(r'\s+', ' ', m.group(1)).strip()
    st = re.sub(r'\s+', ' ', m.group(2)).strip()
    print('## %s' % spec)
    if doc: print('   DOC:', doc[:700])
    print('   STMT:', name, st[:700]); print()

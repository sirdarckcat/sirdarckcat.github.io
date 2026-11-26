#!/usr/bin/env python3
"""Extract theorem statements from *Statement.lean files and tag number-theoretic ones.
Usage: python3 -I stmts.py <src_dir> <out_dir>"""
import os, re, sys, json
SRC, OUT = sys.argv[1], sys.argv[2]
THM = re.compile(r'theorem\s+([^\s:]+)\s*(.*?)(?::=\s*by\b|:=\s*\n|:=\s*[A-Za-z@(])', re.S)
TAGS = {
 'prime':       r'Nat\.Prime|\.Prime\b|Prime\s+[a-z]|Nat\.primeCounting|Nat\.nth',
 'totient':     r'totient',
 'congruence':  r'\[MOD |ModEq|ZMod|Nat\.ModEq',
 'log':         r'Real\.log',
 'arith_fn':    r'ArithmeticFunction|vonMangoldt|Λ|\bμ\b|moebius|cardDistinctFactors|Nat\.factorization|padicValNat',
 'dirichlet':   r'DirichletCharacter|LFunction|riemannZeta|dirichletSummand|DirichletConvolution',
 'finset_sum':  r'Finset\.(sum|Ioc|Icc|range|filter)|∑',
 'polynomial':  r'Polynomial|MvPolynomial|aeval|Polynomial\.eval',
 'sieve':       r'[Ss]ieve|Squarefree|Nat\.Coprime|IsCoprime|Coprime',
 'asymptotic':  r'Asymptotics|IsBigO|isBigO|Filter\.atTop|atTop|Tendsto',
}
trx = {k: re.compile(v) for k, v in TAGS.items()}
CUSTOM_HINTS = re.compile(r'GlobalTheory|Formalism\.|UpperTheory|PositivityTheory|ReciprocityTheory|Hecke|Theta|Adl\b|Cusp|IrrGL|Place\b|HeightOneSpectrum|Iwasawa|Weil|Satake|Hodge|Galois|Frobenius|Shimura|Abelian|Group G|Representation')
rows = []
for r, _, fs in os.walk(SRC):
    for f in fs:
        if not f.endswith('Statement.lean'):
            continue
        p = os.path.join(r, f)
        try:
            t = open(p, errors='replace').read()
        except Exception:
            continue
        m = THM.search(t)
        if not m:
            continue
        name, st = m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip()
        tags = [k for k, g in trx.items() if g.search(st)]
        custom = bool(CUSTOM_HINTS.search(st))
        rows.append({'module': os.path.relpath(p, SRC)[:-5].replace(os.sep, '.'), 'name': name, 'stmt': st[:1500], 'tags': tags, 'custom': custom, 'len': len(st)})
json.dump(rows, open(os.path.join(OUT, 'statements.json'), 'w'), ensure_ascii=False)
print('statements extracted:', len(rows))
import collections
c = collections.Counter()
for x in rows:
    for t in x['tags']:
        c[t] += 1
print('tag counts:', dict(c))
nt = [x for x in rows if ('prime' in x['tags'] or 'totient' in x['tags'] or 'arith_fn' in x['tags'] or 'sieve' in x['tags']) and not x['custom']]
print('number-theoretic & no custom vocabulary:', len(nt))

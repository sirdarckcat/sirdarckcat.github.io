#!/usr/bin/env python3
"""Map the note's timeline ingredients to archive areas by name search.
Usage: python3 -I timeline.py <out_dir>"""
import json, sys, os, re, collections
OUT = sys.argv[1]
TERMS = collections.OrderedDict([
 ('Stepanov',            r'stepanov'),
 ('Deuring / CM supersingular', r'deuring|supersingular'),
 ('invariant derivation / Serre-Tate/Katz', r'serretate|serre_tate|invariantderiv|hasseinvariant|katz'),
 ('Weil positivity / explicit formula / Guinand', r'guinand|weilpositiv|explicitformula|explicit_formula|weildistribution'),
 ('theta lifts', r'thetalift|theta_lift|thetapairlift|thetacorrespondence'),
 ('Chowla-Selberg', r'chowla'),
 ('Siegel-Weil / mass formula', r'siegelweil|siegel_weil|massformula|genusmass'),
 ('seesaw / Rallis / Bessel period', r'seesaw|rallis|besselperiod|besselmodel'),
 ('Gan-Gross-Prasad', r'ggp|gangrossprasad'),
 ('Bost / slope inequality / Harder-Narasimhan', r'bost|slopeinequal|harder.?narasimhan|latticeslope|arakelov'),
 ('Iwasawa tower', r'iwasawatower|iwasawa_tower|iwasawa'),
 ('Behrend', r'behrend'),
 ('Vandiver / K-groups', r'vandiver|kgroup|k_group|algebraickthe|milnor'),
 ('relative trace formula', r'relativetrace|relative_trace|tracef'),
 ('Poincare series', r'poincare'),
 ('Kloosterman/Katz sums, Deligne', r'kloosterman|deligne|weilconjecture|weil_conj|rh_over'),
 ('Hodge theory / p-adic Hodge', r'padichodge|crystalline|semistable|fontaine|wach'),
 ('Hormander L2 dbar', r'dbar|hormander|l2dbar'),
 ('Lubin-Tate / formal groups', r'lubintate|formalgroup'),
 ('Hecke characters / CM fields', r'heckechar|cmfield|iscmfield'),
 ('pigeonhole / Turan power sum', r'pigeonhole|turan'),
 ('von Mangoldt / Chebyshev psi', r'vonmangoldt|chebyshevpsi|mangoldt'),
])
rx = {k: re.compile(v, re.I) for k, v in TERMS.items()}
cnt = collections.Counter(); areas = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
for line in open(os.path.join(OUT, 'index.jsonl')):
    r = json.loads(line)
    m = r['module']
    names = [n for _, n in r['decls']][:400]
    for k, g in rx.items():
        hit = g.search(m)
        if not hit:
            for n in names:
                if g.search(n):
                    hit = n; break
        if hit:
            cnt[k] += 1
            areas[k]['.'.join(m.split('.')[:2])] += 1
            if len(ex[k]) < 2:
                ex[k].append(m.split('.')[-1][:50])
for k in TERMS:
    print('%-46s %6d  top: %s' % (k, cnt[k], '; '.join('%s(%d)' % (a.replace('Development.', 'Dev.'), n) for a, n in areas[k].most_common(3))))

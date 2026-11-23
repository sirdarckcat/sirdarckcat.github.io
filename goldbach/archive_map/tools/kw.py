#!/usr/bin/env python3
"""Keyword scan over module names, declaration names and named-Prop text.
Usage: python3 -I kw.py <out_dir>"""
import json, sys, os, re, collections
OUT = sys.argv[1]
KW = {
 'sieve':            r'sieve|selberg|brun|buchstab|eratosthenes|inclusionexclusion|inclusion_exclusion',
 'large sieve':      r'largesieve|large_sieve',
 'primes/AP':        r'primesinprogress|dirichlet_?thm|exists_?prime|infinitely_?many_?prime|prime_?counting|chebyshev|primeCounting|vonMangoldt|Lambda|mangoldt',
 'Linnik/BV/zero-density': r'linnik|bombieri|vinogradov|zerodensity|zero_?density|log.?free|repulsion|deuring|heilbronn|siegel_?zero|exceptional_?zero|landau',
 'zero-free region': r'zerofree|zero_free',
 'mobius/liouville/parity': r'mobius|moebius|liouville|parity|chowla|sarnak',
 'Goldbach/twin/k-tuples': r'goldbach|twin_?prime|primetuple|prime_?k|dickson|hardylittlewood|admissible_?set|admissible_?tuple|singular_?series',
 'covering systems': r'covering_?system|coveringsystem|exact_?cover|setcover|set_cover',
 'CRT': r'chinese|crt\b|chineseremainder',
 'smooth numbers': r'smooth_?num|ysmooth|isSmooth|rough_?num',
 'primality': r'pocklington|pratt|miller|rabin|ecpp|primality|isprime',
 'lattice/LLL/Coppersmith': r'coppersmith|\bLLL\b|lll_|latticereduction|lattice_?reduction|shortestvector|minkowski|geometryofnumbers',
 'list decoding/RS': r'listdecod|reedsolomon|reed_solomon|guruswami|errorcorrect|decoding',
 'Stepanov/multiplicity': r'stepanov|multiplicity|hasse_?deriv|hasseDeriv|auxiliarypoly|auxiliary_poly',
 'Weil/Kloosterman/char sums': r'kloosterman|gausssum|gauss_?sum|characterbound|exponential_?sum|expsum|weilbound|hasseweil|hasse_weil',
 'Chebotarev/Frobenius': r'chebotarev|frobeniusdensity|frobenius_?orbit',
 'explicit formula': r'explicit_?formula|guinand|weilpositiv|positivity_?crit|trace_?formula',
 'effective/explicit constants': r'explicitconst|effective|explicit_bound',
 'subset sums/counting': r'subset_?sum|subsetsum',
 'function field analog': r'functionfield|function_field|\bF_q\b|polynomialring',
}
rx = {k: re.compile(v, re.I) for k, v in KW.items()}
cnt = collections.Counter(); samples = collections.defaultdict(list); mods = collections.defaultdict(collections.Counter)
for line in open(os.path.join(OUT, 'index.jsonl')):
    r = json.loads(line)
    m = r['module']
    blob_names = [n for _, n in r['decls']]
    for k, g in rx.items():
        hit = None
        if g.search(m):
            hit = ('mod', m)
        else:
            for n in blob_names:
                if g.search(n):
                    hit = ('decl', n); break
        if hit:
            cnt[k] += 1
            mods[k]['.'.join(m.split('.')[:3])] += 1
            if len(samples[k]) < 6:
                samples[k].append((hit[0], hit[1], m))
for k in KW:
    print('=== %s : %d modules' % (k, cnt[k]))
    print('    top areas:', mods[k].most_common(4))
    for kind, name, m in samples[k][:4]:
        print('    -', kind, name[:90], '  [', m[:110], ']')

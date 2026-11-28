#!/usr/bin/env python3
"""Scan every declaration for Mertens-type content. python3 -I mertens_scan.py <src_dir> <out_json>"""
import os, re, sys, json
from multiprocessing import Pool
SRC, OUT = sys.argv[1], sys.argv[2]
DECL = re.compile(r'^(?:@\[[^\]\n]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*(theorem|lemma|def|abbrev|structure|class|inductive|instance|axiom|opaque)\s+([^\s:\(\{\[⦃]+)', re.M)
PRIME = re.compile(r'Nat\.Prime|\.Prime\b|primesLE|primeFactors|Nat\.primes|vonMangoldt|Λ|primeCounting|Nat\.Primes|Prime p|IsPrime')
GAMMA = re.compile(r'eulerMascheroni|euler_mascheroni')
PROD = re.compile(r'(?:∏|Finset\.prod|∏ᶠ|∏\')')
ONE_SUB = re.compile(r'1\s*-\s*(?:\(?\s*1\s*/\s*\(?\s*\(?\s*p|\(?\s*\(?p\s*:\s*[ℝℚℂ]\)?\s*\)?\s*⁻¹|\(?\s*1\s*/\s*p|p\s*\^\s*\(?-1)')
LOGLOG = re.compile(r'Real\.log\s*\(\s*Real\.log')
INVP = re.compile(r'1\s*/\s*\(?\s*\(?\s*p|\(p\s*:\s*[ℝℚℂ]\)\s*⁻¹|p⁻¹|1\s*/\s*\(?\s*\(?\s*q')
NAME = re.compile(r'[Mm]ertens|[Mm]eissel|mertensThird|prod_one_sub_inv|one_sub_inv_prime')

def scan(path):
    try:
        t = open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return []
    ms = list(DECL.finditer(t)); out = []
    mod = os.path.relpath(path, SRC)[:-5].replace(os.sep, '.')
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        seg = t[m.start():end]
        head = seg[:2200]
        tags = []
        if GAMMA.search(head) and PRIME.search(head): tags.append('gamma+prime')
        if PROD.search(head) and PRIME.search(head) and ONE_SUB.search(head): tags.append('prod(1-1/p)')
        if LOGLOG.search(head) and PRIME.search(head) and INVP.search(head): tags.append('loglog+1/p')
        if NAME.search(m.group(2)) or NAME.search(mod.split('.')[-1]): tags.append('name')
        if tags:
            out.append({'module': mod, 'kind': m.group(1), 'name': m.group(2), 'tags': tags, 'text': re.sub(r'\s+', ' ', head[:900])})
    return out

def main():
    files = []
    for r, _, fs in os.walk(SRC):
        for f in fs:
            if f.endswith('.lean'): files.append(os.path.join(r, f))
    res = []
    with Pool(4) as p:
        for o in p.imap(scan, files, chunksize=64): res.extend(o)
    json.dump(res, open(OUT, 'w'), ensure_ascii=False)
    import collections
    c = collections.Counter(t for r in res for t in r['tags'])
    print('hits:', len(res), dict(c))
main()

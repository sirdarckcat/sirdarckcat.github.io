import pickle, sys
d2m, m2p = pickle.load(open('lg/decls.pkl','rb'))
names = sys.argv[1:]
for s in names:
    c = sorted([n for n in d2m if n == s or n.endswith('.'+s)], key=len)
    if not c: print('!! NOT FOUND', s)
    else: print('%-60s -> %s   [%s]%s' % (s, c[0], d2m[c[0]].replace('GoldbachGaps.',''), ('  (+%d)' % (len(c)-1)) if len(c)>1 else ''))

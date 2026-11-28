"""The cover-first prefix as residues modulo M0 = 2 3 5 ... 23: prefix_C.u32 holds the residues N mod M0 of the members
with at most C rows left at depth 23 (the rows left at depth 23 depend on N mod M0 only)."""
import sys
import numpy as np
import pp
M0 = 223092870
N = np.asarray(pp.N); k1 = np.asarray(pp.K1)
for c in map(int, sys.argv[1:]):
    sel = N[k1 <= c]
    r = np.unique(sel % M0).astype(np.uint32)
    r.tofile(f"data/prefix_{c}.u32")
    print(f"rows left at depth 23 <= {c}: {len(sel):,d} members, {len(r):,d} residues modulo M0", flush=True)

import math
from base import *
dl = {r: dlt_table(r) for r in cprimes}
for j, sg in ((5, 4), (6, 5), (6, 4), (7, 7)):
    later = LATER[:j]; hit = {s: hit_table(s) for s in later}
    ncov = sum(int((dl[r] <= sg).sum()) for r in cprimes if (dl[r] <= sg).sum() > 1)
    nlat = sum(int(((hit[s].max() - hit[s]) <= sg).sum()) for s in later)
    E = sg + 1 + j; P = M * prod(later); B = -((-E * P) // X)
    print(f"j={j} sigma={sg}: cover classes kept {ncov}, later classes kept {nlat}, total {ncov + nlat}; E={E} B={B} ({B * X / P:.2f} e^D); B*classes = {B * (ncov + nlat):.4g}")

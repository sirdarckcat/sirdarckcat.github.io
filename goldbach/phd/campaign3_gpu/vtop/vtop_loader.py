#!/usr/bin/env python3
"""The lead's conditions 1 and 4 for --vector-place top, on the code itself: production's VectorSource and load_specs (search_gpu5.py) and the patched ones
(search_gpu5_vtop.py), each exec'd from its own file, on a snapshot of the vector chunk files with the campaign's done set (its search.log), one chunk at a time:
  bottom (patched, default) == production: the same slices (name, kstart, kmax) from every chunk, the same skipped count;
  top: every window inside [10^199, 10^200) and ending at the vector's last 200-digit k (recomputed here: kend = min(kmax, ceil((10^200 - N0) / M))); no vector taken twice;
       exactly the vectors bottom takes (none skipped, none added); none whose name is in the done set under either placement; a restart after some top windows
       (their names in the done set) takes them neither at the top nor at the bottom.
    python3 vtop_loader.py PROD_DRIVER PATCHED_DRIVER VEC_SNAPSHOT_DIR CAMPAIGN_SEARCH_LOG"""
import ast, collections, glob, json, os, re, sys, time
from gmpy2 import mpz

def load(path):
    tree = ast.parse(open(path).read())
    keep = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in ("VectorSource", "load_specs")]
    ns = dict(mpz=mpz, glob=glob, os=os, collections=collections, json=json, time=time)
    exec(compile(ast.Module(body=keep, type_ignores=[]), path, "exec"), ns)
    return ns["VectorSource"]

PROD, NEW, V, LOG = sys.argv[1:5]
K = 1 << 24
done = {m.group(1) for m in map(re.compile(r"\[(\S+)\] k=\[").match, open(LOG)) if m}
bases_done = {x.split("@")[0] for x in done}
t0 = time.time()
P, B, T = load(PROD)(V, K, 200, 0), load(NEW)(V, K, 200, 0, "bottom"), load(NEW)(V, K, 200, 0, "top")
lo, hi = mpz(10) ** 199, mpz(10) ** 200
nfiles = ok_same = 0; bad = []; top_names, top_bases, bot_bases, all_bases = [], set(), set(), []
kst = collections.Counter(); nmin = nmax = None; coincide = 0
specs_by_name = {}
while True:
    rp, rb, rt = P._load_next(done), B._load_next(done), T._load_next(done)
    if not (rp or rb or rt):
        break
    assert rp == rb == rt, "the three loaders went out of step"
    nfiles += 1
    qp = [(x["name"], x["kstart"], x["kmax"]) for x in P.queue]; qb = [(x["name"], x["kstart"], x["kmax"]) for x in B.queue]
    if qp == qb:
        ok_same += 1
    else:
        bad.append(("bottom != production", nfiles, len(qp), len(qb)))
    f = sorted(glob.glob(os.path.join(V, "vec_*.json")))[nfiles - 1]
    raw = {s["name"]: (mpz(s["N0"]), mpz(s["M"]), int(s["kmax"])) for s in json.load(open(f))}
    all_bases.extend(raw)
    for x in B.queue:
        bot_bases.add(x["name"].split("@")[0])
    for x in T.queue:
        b, ks = x["name"].split("@"); ks = int(ks)
        N0, M, kmax = raw[b]
        kend = min(kmax, int((hi - N0 + M - 1) // M))
        k_lo = int((lo - N0 + M - 1) // M)
        if not (ks == x["kstart"] == kend - K and x["kmax"] == kend and N0 + ks * M >= lo and N0 + (kend - 1) * M < hi and (N0 + kend * M >= hi or kend == kmax)):
            bad.append(("top window", b, ks, kend))
        if b in bases_done:
            bad.append(("top takes a done vector", b))
        if b in top_bases:
            bad.append(("top takes a vector twice", b))
        top_bases.add(b); top_names.append(x["name"]); kst[ks] += 1
        n_a, n_b = N0 + ks * M, N0 + (kend - 1) * M
        nmin = n_a if nmin is None or n_a < nmin else nmin; nmax = n_b if nmax is None or n_b > nmax else nmax
        coincide += (ks == k_lo)
    P.queue.clear(); B.queue.clear(); T.queue.clear()
print(f"[ld] {nfiles} chunk files, {len(all_bases)} vectors ({len(set(all_bases))} distinct names), done set {len(done)} slices ({len(bases_done)} vectors) | {time.time() - t0:.0f} s")
print(f"[ld] bottom (patched) == production on {ok_same} of {nfiles} chunks | skipped: production {P.skipped}, bottom {B.skipped}, top {T.skipped}")
print(f"[ld] top: {len(top_names)} windows, {len(top_bases)} distinct vectors | the same vectors as bottom: {top_bases == bot_bases} | done vectors among them: {len(top_bases & bases_done)}"
      f" | not done and not taken: {len(set(all_bases) - bases_done - top_bases)} | kstart values {dict(kst.most_common(4))} | window = bottom's for {coincide}")
print(f"[ld] top N range: {float(nmin):.4e} .. {float(nmax):.10e} (10^200 = 1e200: below: {nmax < hi}; 200 digits: {nmin >= lo})" if nmin is not None else "[ld] top: no windows")
# a restart after the first nr top windows were done: neither placement takes them again
nr = min(1000, len(top_names) // 2)
done2 = done | set(top_names[:nr]); first = {n.split("@")[0] for n in top_names[:nr]}
T2, B2 = load(NEW)(V, K, 200, 0, "top"), load(NEW)(V, K, 200, 0, "bottom")
again_t = again_b = 0; n_t2 = 0
while T2._load_next(done2) | B2._load_next(done2):
    again_t += sum(x["name"].split("@")[0] in first for x in T2.queue); n_t2 += len(T2.queue)
    again_b += sum(x["name"].split("@")[0] in first for x in B2.queue)
    T2.queue.clear(); B2.queue.clear()
print(f"[ld] restart with {nr} top windows done: top takes {n_t2} ({len(top_names) - nr} expected), {again_t} of the {nr} again; bottom takes {again_b} of them")
ok = bool(top_names) and not bad and ok_same == nfiles and P.skipped == B.skipped == T.skipped and top_bases == bot_bases and not (top_bases & bases_done) \
     and n_t2 == len(top_names) - nr and again_t == 0 and again_b == 0 and len(set(all_bases)) == len(all_bases)
print("[ld] problems:", bad[:5])
print("[ld] LOADER", "PASSED" if ok else "FAILED")

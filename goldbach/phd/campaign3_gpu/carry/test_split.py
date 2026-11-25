"""SplitOut (--record) with the carry path's DedupOut on top, taken from the patched engine itself: routing by g, each N once, across a restart."""
import ast, json, os, sys, tempfile
eng = sys.argv[1]
tree = ast.parse(open(eng).read())
cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in ("SplitOut", "DedupOut")]
ns = {"json": json, "os": os}
exec(compile(ast.Module(body=cls, type_ignores=[]), eng, "exec"), ns)
d = tempfile.mkdtemp()
F, NE = os.path.join(d, "found.jsonl"), os.path.join(d, "near_events.jsonl")
recs = [dict(N="1", g=150001, near_miss=True), dict(N="2", g=160357, near_miss=True), dict(N="3", g=160361, near_miss=True), dict(N="4", g=171001),
        dict(N="5", g=140009, near_miss=True, kernel_discrepancy=True, claimed_q=139999), dict(N="1", g=150001, near_miss=True)]
def run(seen_from_found):
    so = ns["SplitOut"](F, NE, 160357)
    seen = set(json.loads(l)["N"] for l in open(F)) if (seen_from_found and os.path.exists(F)) else set()
    do = ns["DedupOut"](so, seen)
    for r in recs:
        do.write(json.dumps(r) + "\n"); do.flush()
    return do.written
w1 = run(False)
w2 = run(True)                                            # a restart that redoes every slice
fl = [json.loads(l) for l in open(F)]; nl = [json.loads(l) for l in open(NE)]
ok = sorted(x["N"] for x in fl) == ["3", "4"] and sorted(x["N"] for x in nl) == ["1", "2", "5"] and all(x.get("sub_record") for x in nl) and not any("sub_record" in x for x in fl)
print(f"first run wrote {w1}, restart wrote {w2} (DedupOut counts); found.jsonl {[(x['N'], x['g']) for x in fl]}; near_events.jsonl {[(x['N'], x['g']) for x in nl]}")
print("SPLIT-TEST", "PASSED" if ok else "FAILED")

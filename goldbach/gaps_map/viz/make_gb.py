import json, re, os, collections, sys
V = os.path.dirname(os.path.abspath(__file__))
def load(fn, name):
    ns = {"__file__": os.path.join(V, fn)}
    exec(open(os.path.join(V, fn)).read(), ns)
    return ns[name]
NODES = {}
for fn, nm in (("cur_lean1.py", "N1"), ("cur_lean2.py", "N2"), ("cur_lean4.py", "N4"), ("cur_lean5.py", "N5")):
    NODES.update(load(fn, nm))
NODES["c_brainstorm"] = load("cur_lean3.py", "N3")["c_brainstorm"] if os.path.exists(os.path.join(V, "cur_lean3.py")) else None
NODES = {k: v for k, v in NODES.items() if v}
LEAN = load("spec_lean.py", "LEAN"); ALSO = load("spec_lean.py", "ALSO")
E_LEAN = load("cur_edges_lean.py", "E_LEAN")
_e5 = load("cur_edges_lean5.py", "E_LEAN5"); _drop = load("cur_edges_lean5.py", "E_DROP")
assert not (set(_e5) & set(E_LEAN)), ("new lean edge text collides with an old one", sorted(set(_e5) & set(E_LEAN)))
E_LEAN.update(_e5)
for _k in _drop: E_LEAN.pop(_k)
RES_NODES, RES_EDGES = {}, {}
if os.path.exists(os.path.join(V, "cur_res.py")):
    RES_NODES = load("cur_res.py", "R_NODES"); RES_EDGES = load("cur_res.py", "R_EDGES")
# ---- patches to boxes that existed in the previous map (cur_patch.py): fields replaced or appended, and marked as updated
PATCH = load("cur_patch.py", "PATCH") if os.path.exists(os.path.join(V, "cur_patch.py")) else {}
for pid, pp in PATCH.items():
    tgt = NODES.get(pid) or RES_NODES.get(pid)
    assert tgt is not None, ("patch for an unknown box", pid)
    for k, v in pp.items():
        if k == "repl":
            for fld, pairs in v.items():
                for old, new in pairs:
                    assert old in tgt.get(fld, ""), ("patch text not found", pid, fld, old[:50])
                    tgt[fld] = tgt[fld].replace(old, new)
        elif k == "detail_add": tgt["detail"] = (tgt.get("detail", "") + " " + v).strip()
        elif k == "note_add": tgt["note"] = (tgt.get("note", "") + " " + v).strip()
        elif k == "chips_add": tgt["chips"] = list(tgt.get("chips", [])) + list(v)
        else: tgt[k] = v
    tgt.setdefault("since", "upd")
META = load("meta.py", "META"); GROUPS = load("meta.py", "GROUPS"); LENSES = load("meta.py", "LENSES")
raw = json.load(open(os.path.join(V, "graph_lean.json"))); direct = json.load(open(os.path.join(V, "direct_lean.json")))
assert set(NODES) >= set(LEAN), ("lean nodes without curation", sorted(set(LEAN) - set(NODES)))
extra = set(NODES) - set(LEAN)
assert not extra, ("curated lean nodes not in spec", extra)
gids = {g["id"] for g in GROUPS}
def short(x): return x.replace("GoldbachGaps.", "")
def path_of(module):
    return "goldbach/lean/" + module.replace(".", "/") + ".lean"
nodes = []
for i in LEAN:
    c = NODES[i]; info = raw["info"][i]
    assert c["group"] in gids, (i, c["group"])
    src = re.sub(r"\n{2,}", "\n", info["source"]).strip()
    if len(src) > 1000: src = src[:1000].rstrip() + "\n..."
    meta = [["Lean name", short(info["decl"]), True], ["File", path_of(info["module"]), True]]
    if ALSO.get(i): meta.append(["Also covers", ", ".join(short(a) for a in ALSO[i]), False])
    n = dict(id=i, group=c["group"], title=c["title"], gist=c["gist"], detail=c.get("detail", ""), chips=c.get("chips", []),
             f=dict(status=c["status"], impact=c["impact"], since=c.get("since", "old")), meta=meta, source=src, sourceLabel="Lean statement and proof (first lines)",
             search=short(info["decl"]) + " " + " ".join(short(a) for a in ALSO.get(i, [])) + " " + info["module"].split(".")[-1])
    if c.get("note"): n["note"] = dict(level=c["impact"], text=c["note"])
    nodes.append(n)
for i, c in RES_NODES.items():
    assert c["group"] in gids, (i, c["group"])
    n = dict(id=i, group=c["group"], title=c["title"], gist=c["gist"], detail=c.get("detail", ""), chips=c.get("chips", []),
             f=dict(status=c["status"], impact=c["impact"], since=c.get("since", "old")), meta=[[k, v, False] for k, v in c.get("where", [])], search=c.get("search", ""))
    if c.get("note"): n["note"] = dict(level=c["impact"], text=c["note"])
    if c.get("source"): n["source"] = c["source"]; n["sourceLabel"] = c.get("sourceLabel", "Quoted from the document")
    nodes.append(n)
ids = [n["id"] for n in nodes]
assert len(ids) == len(set(ids)), "duplicate node ids"
idset = set(ids)
# ---- edges
edges = {}
tool_direct = {(e["from"], e["to"]) for e in direct["direct"]}
for (a, b) in tool_direct:
    edges[(a, b)] = dict(kind="direct", hops=1, chain=[])
for e in raw["edges"]:
    k = (e["from"], e["to"])
    if k not in edges:
        edges[k] = dict(kind="indirect", hops=len(e["path"]) - 1, chain=[short(x) for x in e["path"]])
out = []; missing = []
for (a, b), e in sorted(edges.items()):
    key = a + ">" + b
    if key not in E_LEAN: missing.append(key); continue
    t = E_LEAN[key]
    assert len(t) == 2, ("tool-found edge must not carry kind/source", key)
    out.append(dict(id=key, **{"from": a, "to": b}, kind=e["kind"], hops=e["hops"], chain=e["chain"], short=t[0], why=t[1]))
assert not missing, ("lean edges without text", missing)
hand = {k: v for k, v in E_LEAN.items() if len(v) == 4}
toolkeys = {a + ">" + b for (a, b) in edges}
for key, t in hand.items():
    assert key not in toolkeys, ("hand edge duplicates a tool edge", key)
    a, b = key.split(">")
    out.append(dict(id=key, **{"from": a, "to": b}, kind=t[2], hops=1, chain=[], short=t[0], why=t[1], source=t[3]))
unused = [k for k, v in E_LEAN.items() if len(v) == 2 and k not in toolkeys]
assert not unused, ("curated lean edges the tool did not find", unused)
for key, t in RES_EDGES.items():
    a, b = key.split(">")
    kind = t[2] if len(t) > 2 else "doc"
    out.append(dict(id=key, **{"from": a, "to": b}, kind=kind, hops=1, chain=[], short=t[0], why=t[1], **({"source": t[3]} if len(t) > 3 else {})))
for e in out:
    assert e["from"] in idset and e["to"] in idset, ("edge endpoint missing", e["id"])
assert len({e["id"] for e in out}) == len(out), "duplicate edge ids"
# ---- connectivity and DAG
deg = collections.Counter()
for e in out: deg[e["from"]] += 1; deg[e["to"]] += 1
iso = [i for i in ids if deg[i] == 0]
outs = collections.defaultdict(list); ins = collections.defaultdict(list)
for e in out: outs[e["from"]].append(e["to"]); ins[e["to"]].append(e["from"])
indeg = {i: len(ins[i]) for i in ids}; q = [i for i in ids if indeg[i] == 0]; order = []
while q:
    x = q.pop(0); order.append(x)
    for y in outs[x]:
        indeg[y] -= 1
        if indeg[y] == 0: q.append(y)
cyc = [i for i in ids if i not in set(order)]
layer = {}
for x in order: layer[x] = max([layer[p] + 1 for p in ins[x]], default=0)
cols = collections.Counter(layer.values())
print("nodes", len(nodes), "edges", len(out), dict(collections.Counter(e["kind"] for e in out)))
print("isolated:", iso); print("cycle members:", cyc)
print("layers:", [cols[i] for i in range(max(cols) + 1)] if cols else [])
nl = sum(1 for n in nodes if n["id"] in LEAN); nr = len(nodes) - nl
META = dict(META); META["statsHTML"] = META["statsHTML"].replace("{NODES}", str(len(nodes))).replace("{EDGES}", str(len(out))).replace("{LEAN}", str(nl)).replace("{RES}", str(nr))
data = dict(meta=META, groups=GROUPS, lenses=LENSES, nodes=nodes, edges=out)
json.dump(data, open(os.path.join(V, "gb_data.json"), "w"), ensure_ascii=False)
if iso or cyc: sys.exit("fix isolated/cycle nodes before building the page")
t = open(os.path.join(V, "page_template.html")).read()
assert "/*DATA*/" in t
js = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
t = t.replace("/*DATA*/", js).replace("/*PAGETITLE*/", META["pageTitle"]).replace("/*H1*/", META["h1"]).replace("/*SUB*/", META["sub"]).replace("/*MAPLABEL*/", META["mapLabel"]).replace("/*PLACEHOLDER*/", META["placeholder"])
open(os.path.join(V, "goldbach_map.html"), "w").write(t)
print("page bytes", len(t))
skel = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)} body{margin:0;font:14px system-ui} [hidden]{display:none!important}</style></head><body>'
if os.environ.get("GB_TEST_SHELL"):
    open(os.environ["GB_TEST_SHELL"], "w").write(skel + t + "</body></html>")  # only for browser tests; not part of the repo

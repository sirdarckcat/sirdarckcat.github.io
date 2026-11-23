import json, re, collections
import os
V = os.path.dirname(os.path.abspath(__file__))
ns = {}; exec(open(V + "/curation_nodes.py").read(), ns); NODES = ns["NODES"]
ns2 = {}; exec(open(V + "/curation_edges.py").read(), ns2); EDGES = ns2["EDGES"]
raw = json.load(open(V + "/graph_raw.json")); direct = json.load(open(V + "/direct.json"))
spec = json.load(open(V + "/spec.json"))
spec_ids = [n["id"] for n in spec["nodes"] if n["id"] != "t_zd"]
GROUPS = [
 ("claim", "Claims", "What the archive says it proves (Main.lean)."),
 ("assembly", "Assembly", "Supplements.Kernels.MainTheorems: aliases and bundles that hand the claims to the argument."),
 ("bridge", "Functional-equation bridge", "Elementary steps from 'no zeros right of 1/2' to the stated claims. Short proofs that I read."),
 ("core", "Main argument", "How the key statement is assembled from deeper results."),
 ("input", "Inputs", "Galois representations, local Langlands, the window estimate and the published inputs."),
 ("classical", "Classical results", "Textbook and published theorems the archive claims to re-prove."),
 ("toolbox", "Number-theory toolbox", "Prime-distribution bounds. The chain from Linnik down to the large sieve lives here."),
]
gids = [g[0] for g in GROUPS]
# node validation
missing = [i for i in spec_ids if i not in NODES]; extra = [i for i in NODES if i not in spec_ids]
assert not missing and not extra, (missing, extra)
def short(name):
    p = name.split(".")
    return ".".join(p[-2:]) if len(p) > 1 else name
nodes = []
for i in spec_ids:
    c = NODES[i]; info = raw["info"][i]
    src = info["source"]
    src = re.sub(r"\n{2,}", "\n", src).strip()
    if len(src) > 900: src = src[:900].rstrip() + "\n..."
    gl, gn = c["gb"]
    nodes.append(dict(id=i, group=c["group"], title=c["title"], gist=c["gist"], detail=c.get("detail", ""), kind=c["kind"], conf=c["conf"],
                      gb=dict(level=gl, note=gn), decl=info["decl"], module=info["module"], source=src))
# edges: all direct among spec nodes + indirect from reduced graph
ids = set(spec_ids)
edges = {}
for e in direct["direct"]:
    if e["from"] in ids and e["to"] in ids:
        edges[(e["from"], e["to"])] = dict(from_=e["from"], to=e["to"], kind="direct", hops=1, chain=[])
for e in raw["edges"]:
    k = (e["from"], e["to"])
    if k[0] in ids and k[1] in ids and k not in edges and not e["direct"]:
        edges[k] = dict(from_=e["from"], to=e["to"], kind="indirect", hops=len(e["path"]) - 1, chain=[short(x) for x in e["path"]])
out_edges = []
miss_text = []
for (a, b), e in sorted(edges.items()):
    key = a + ">" + b
    if key not in EDGES: miss_text.append(key); continue
    s, w = EDGES[key]
    s = re.sub(r"\s*\(\d+ steps?\)", "", s)
    out_edges.append({"id": key, "from": a, "to": b, "kind": e["kind"], "hops": e["hops"], "chain": e["chain"], "short": s, "why": w})
unused = [k for k in EDGES if k not in {e["id"] for e in out_edges}]
assert not miss_text, ("edges without text", miss_text)
assert not unused, ("curated edges that do not exist", unused)
# connectivity check
deg = collections.Counter()
for e in out_edges: deg[e["from"]] += 1; deg[e["to"]] += 1
iso = [i for i in spec_ids if deg[i] == 0]
assert not iso, ("isolated", iso)
# DAG check + layers
outs = collections.defaultdict(list); ins = collections.defaultdict(list)
for e in out_edges: outs[e["from"]].append(e["to"]); ins[e["to"]].append(e["from"])
layer = {}
order = []; indeg = {i: len(ins[i]) for i in spec_ids}; q = [i for i in spec_ids if indeg[i] == 0]
while q:
    x = q.pop(0); order.append(x)
    for y in outs[x]:
        indeg[y] -= 1
        if indeg[y] == 0: q.append(y)
assert len(order) == len(spec_ids), "cycle!"
for x in order:
    layer[x] = max([layer[p] + 1 for p in ins[x]], default=0)
cols = collections.Counter(layer.values())
print("nodes", len(nodes), "edges", len(out_edges), "direct", sum(1 for e in out_edges if e["kind"] == "direct"), "indirect", sum(1 for e in out_edges if e["kind"] == "indirect"))
print("layers (count per column):", [cols[i] for i in range(max(cols) + 1)])
meta = dict(modules=175187, lines=17549402, nodes=len(nodes), edges=len(out_edges),
            direct=sum(1 for e in out_edges if e["kind"] == "direct"), indirect=sum(1 for e in out_edges if e["kind"] == "indirect"))
json.dump(dict(groups=[dict(id=g[0], label=g[1], blurb=g[2]) for g in GROUPS], nodes=nodes, edges=out_edges, meta=meta), open(V + "/viz_data.json", "w"), ensure_ascii=False)
print("wrote viz_data.json", len(open(V + "/viz_data.json").read()) // 1024, "KB")

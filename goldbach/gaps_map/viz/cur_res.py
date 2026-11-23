import os
_V = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
R_NODES = {}
for _fn, _nm in (("cur_res_a.py", "RA"), ("cur_res_b.py", "RB"), ("cur_res_c.py", "RC")):
    _ns = {}
    exec(open(os.path.join(_V, _fn)).read(), _ns)
    R_NODES.update(_ns[_nm])
_ns = {}
exec(open(os.path.join(_V, "cur_res_edges.py")).read(), _ns)
R_EDGES = _ns["R_EDGES"]
# Evidence layer: exhaustive tests of the model (goldbach/archipelagos/), kept in its own file.
_ns = {}
exec(open(os.path.join(_V, "cur_tests.py")).read(), _ns)
assert not (set(_ns["RT"]) & set(R_NODES)), "evidence box id collides with a research box"
assert not (set(_ns["RT_EDGES"]) & set(R_EDGES)), "evidence link collides with a research link"
R_NODES.update(_ns["RT"])
R_EDGES.update(_ns["RT_EDGES"])
for _id, _p in _ns["RT_PATCH"].items():
    _n = R_NODES[_id]
    if "detail" in _p: _n["detail"] = _n.get("detail", "") + _p["detail"]
    if "chips" in _p: _n["chips"] = list(_n.get("chips", [])) + _p["chips"]

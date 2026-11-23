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

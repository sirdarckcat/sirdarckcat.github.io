import json
import os
V = os.path.dirname(os.path.abspath(__file__))
data=open(V+"/viz_data.json").read()
data=data.replace("<","\\u003c").replace("\u2028","\\u2028").replace("\u2029","\\u2029")
t=open(V+"/page_template.html").read()
assert "/*DATA*/" in t
out=t.replace("/*DATA*/",data)
open(V+"/dependency_map.html","w").write(out)
print("page bytes:",len(out))

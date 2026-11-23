# Assemble the chart data and build goldbach-archipelagos.html from page_template.html.
# Inputs are the outputs of theory.py, archipelagos.py, ml.py, budget.py, tail.py, viz_data.py and amap.py.
import json
J = lambda f: json.load(open(f))
am = J("amap_e18.json"); vz = J("viz_e18.json")
ar = {n: J(f"archipelagos_{n}.json") for n in ("e12", "e15", "e18")}
th = {n: J(f"theory_{n}.json") for n in ("e12", "e15", "e18")}
bud = {n: J(f"budget_{n}.json") for n in ("e15", "e18")}
tl = {n: J(f"tail_{n}.json") for n in ("e12", "e15", "e18")}
ml = {k: J(f) for k, f in (("e18_997", "ml_e18_Z997_p1.0.json"), ("e18_97", "ml_e18_Z97_p1.0.json"), ("e15_997", "ml_e15_Z997_p1.0.json"))}
A = am["archipelago"]
B = {
 # 19-digit integers travel as strings: JSON numbers above 2^53 lose precision in JavaScript
 "amap": {"N_min_s": str(A["N_min"]), "N_start_s": str(am["N_start"]), "start_off": am["N_start"] - A["N_min"],
          "g": am["g"], "pb": am["primes_below"], "G": am["G"], "mean_pb": round(am["mean_primes_below"], 2),
          "isl": {"span": A["span"], "size": A["size"], "gmax": A["gmax"]}},
 "lag": [[r["d"], r["measured"], r["model"], r["shared"]] for r in vz["lag"]],
 "cal": [[r["u"], r["n"], r["observed"], r["model"]] for r in vz["calibration"]],
 "c997": vz["c997"],
 "res": {n: {k: v for k, v in ar[n]["residues"].items() if k in ("3", "5", "7")} for n in ar},
 "arch": {n: dict(ar[n]["archipelagos"], theta=ar[n]["theta"], G1=ar[n]["G1"], G3=ar[n]["G3"]) for n in ar},
 "pbtab": ar["e18"]["primes_below"],
 "budget": {n: bud[n]["rows"] for n in bud},
 "tail": {n: tl[n]["rows"] for n in tl},
 "ml": {k: {m: v for m, v in d.items() if isinstance(v, dict)} for k, d in ml.items()},
}
t = open("page_template.html").read()
assert t.count("/*BUNDLE*/null") == 1
open("goldbach-archipelagos.html", "w").write(t.replace("/*BUNDLE*/null", json.dumps(B, separators=(",", ":"))))
print("page bytes", len(open("goldbach-archipelagos.html").read()))

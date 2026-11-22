#!/usr/bin/env python3
"""Turn the smallest success in a state file into a record directory.

    python3 pack.py state.json specs.json

state.json is a vscan.py state (its "found" list) or a scan.py state (one
"found" entry); specs.json is the variants list or the single spec that was
scanned.  The result is ../records/threshold_<digits>digit_g<g>/ with
  record.json, evidence.json   from ../package_record.py: a compositeness
                               witness for N - q for every prime q < g
  complement_cert.gp, check_cert.log   PARI ECPP certificate for N - g
  direct_check.gp, direct_check.log    the whole claim again in PARI, without
                                       the evidence file
  MANIFEST.sha256
It refuses to overwrite an existing directory and stops at the first check
that fails.  Needs gp (PARI) and gmpy2.
"""
import hashlib, json, os, re, subprocess, sys
G = os.environ.get("GOLDBACH_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
st = json.load(open(sys.argv[1]))
fl = st["found"] if isinstance(st["found"], list) else [st["found"]]      # vscan keeps a list, scan.py the first success
found = min(fl, key=lambda f: int(f["N"]))
specs = json.load(open(sys.argv[2]))
spec = next(s for s in (specs if isinstance(specs, list) else [specs]) if s["name"] == found["name"])
N, g = int(found["N"]), int(found["g"])
out = f"records/threshold_{len(str(N))}digit_g{g}"
assert not os.path.exists(os.path.join(G, out)), out
tmp = os.path.dirname(os.path.abspath(sys.argv[1]))
json.dump(found, open(f"{tmp}/found_best.json", "w"))
json.dump([spec], open(f"{tmp}/spec_best.json", "w"))
r = subprocess.run([sys.executable, "package_record.py", f"{tmp}/found_best.json", f"{tmp}/spec_best.json", out + "/"],
                   cwd=G, capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
assert r.returncode == 0
d = os.path.join(G, out)
log = re.sub(r"\x1b\[[0-9;]*m", "", open(f"{d}/check_cert.log").read())
open(f"{d}/check_cert.log", "w").write(log)
assert "valid: 1" in log, log
open(f"{d}/direct_check.gp", "w").write(f'''chk(N, g) = {{
  my(bad = 0, cnt = 0);
  if (N % 2, error("N odd"));
  if (!isprime(g) || !isprime(N - g), error("g or N - g not prime"));
  forprime(q = 2, g - 1, cnt++; if (ispseudoprime(N - q), bad++));
  if (bad, error("a smaller prime works"));
  print("PROVED g(N) = ", g, " for N = ", N, " (", #Str(N), " digits; ", cnt, " smaller primes all give composite N - q)");
}}
chk({N}, {g});
quit
''')
r = subprocess.run("gp -q direct_check.gp < /dev/null > direct_check.log 2>&1", shell=True, cwd=d)
dl = open(f"{d}/direct_check.log").read()
print(dl)
assert r.returncode == 0 and dl.startswith(f"PROVED g(N) = {g} for N = {N} ") and "***" not in dl, dl
names = ["record.json", "evidence.json", "complement_cert.gp", "check_cert.log", "direct_check.gp", "direct_check.log"]
with open(f"{d}/MANIFEST.sha256", "w") as f:
    for n in names:
        f.write(hashlib.sha256(open(f"{d}/{n}", "rb").read()).hexdigest() + "  " + n + "\n")
ev = json.load(open(f"{d}/evidence.json"))
print("packaged", out, {k: v for k, v in ev.items() if not isinstance(v, (list, dict))})
print("found:", {k: found[k] for k in ("name", "N", "digits", "g", "k")}, "residual primes:", len(spec["residual"]))

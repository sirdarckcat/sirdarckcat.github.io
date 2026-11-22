#!/bin/bash
# certify_c3.sh FOUND_JSONL SPECS_JSON [OUTROOT]
# Certify the first line of a campaign3 found.jsonl (search_gpu3.py / search.py output):
#   1. N = N0 + k*M from the variant's spec (name before '@'); N even, N < 10^199, equal to the logged N;
#   2. goldbach/package_record.py: record.json, evidence.json (a witness for every prime q < g),
#      complement_cert.gp (PARI primecert of N - g) and check_cert.log (primecertisvalid);
#   3. goldbach/ecpp_check.py: the certificate re-verified without PARI;
#   4. slop/goldbach/records/verify_record.py (stdlib only): N from the congruences and t = k, every p < g,
#      the certificate again, and the claims g > CLAIM_Q (default 119,419), digits <= CLAIM_DIGITS (default 200), N < 10^200;
#   5. a direct gmpy2 check and a direct PARI check (ispseudoprime for p < g, isprime(N - g));
#   6. MANIFEST.sha256.
# Output: OUTROOT/budget_1e200_<digits>digit_g<g>/ (OUTROOT defaults to goldbach/records).
set -u
R=/home/user/sirdarckcat.github.io
G=$R/goldbach
OUTROOT=${3:-$G/records}
W=$(mktemp -d)
python3 - "$1" "$2" "$W" <<'EOF' || { echo "CERTIFY-FAILED at the spec step"; exit 1; }
import json, sys
f = json.loads(open(sys.argv[1]).read().strip().splitlines()[0])
base = f["name"].split("@")[0]
specs = json.load(open(sys.argv[2]))
specs = specs if isinstance(specs, list) else [specs]
sp = next(s for s in specs if s["name"] in (base, f["name"]))
sp = dict(sp, name=f["name"])
for fld in ("residual", "cover"):
    if isinstance(sp.get(fld), str):
        sp[fld] = json.loads(sp[fld])
sp["Q"] = int(sp["Q"])
N = int(sp["N0"]) + int(f["k"]) * int(sp["M"])
assert str(N) == str(f["N"]), "N0 + k*M differs from the logged N"
assert N % 2 == 0
D = len(str(N))
json.dump(f, open(sys.argv[3] + "/found.json", "w"))
json.dump([sp], open(sys.argv[3] + "/spec.json", "w"))
open(sys.argv[3] + "/dir", "w").write(f"budget_1e200_{D}digit_g{f['g']}")
print(f"[cert] {f['name']} k={f['k']} digits={D} g={f['g']} below 10^199: {N < 10**199}, below 10^200: {N < 10**200}")
EOF
OUT=$OUTROOT/$(cat $W/dir)
mkdir -p $OUT
cd $G
echo "[cert] 2. package_record.py -> $OUT"
python3 package_record.py $W/found.json $W/spec.json $OUT || echo "CERTIFY-FAILED package_record"
python3 -c "import json; f=json.load(open('$W/found.json')); print(int(f['N']) - int(f['g']))" > $OUT/N_minus_g.txt
echo "[cert] 3. ecpp_check.py"
python3 ecpp_check.py $OUT/complement_cert.gp $OUT/N_minus_g.txt > $OUT/ecpp_check.log 2>&1; tail -n 1 $OUT/ecpp_check.log
echo "[cert] 4. slop verify_record.py (stdlib only)"
python3 - "$W" "$OUT" <<'EOF'
import json, os, re, sys
W, OUT = sys.argv[1], sys.argv[2]
f = json.load(open(W + "/found.json")); sp = json.load(open(W + "/spec.json"))[0]
cert = json.loads(re.sub(r"\s+", "", open(OUT + "/complement_cert.gp").read()))
pkg = {"N": str(f["N"]), "q": int(f["g"]), "classes": sp["cover"], "t": int(f["k"]), "ecpp_cert": cert,
       "claims": {"q_exceeds": int(os.environ.get("CLAIM_Q", "119419")), "digits_at_most": int(os.environ.get("CLAIM_DIGITS", "200")),
                  "N_below": str(10 ** 200)}}
json.dump(pkg, open(OUT + "/package_stdlib.json", "w"))
EOF
python3 $R/slop/goldbach/records/verify_record.py $OUT/package_stdlib.json > $OUT/verify_stdlib.log 2>&1; echo "rc=$?" >> $OUT/verify_stdlib.log; tail -n 3 $OUT/verify_stdlib.log
echo "[cert] 5. direct checks"
python3 - "$W" "$OUT" <<'EOF'
import json, sys, time
import gmpy2
from gmpy2 import mpz, is_prime
from sympy import primerange
W, OUT = sys.argv[1], sys.argv[2]
f = json.load(open(W + "/found.json"))
N, g = mpz(f["N"]), int(f["g"])
t0 = time.time()
bad = [p for p in primerange(2, g) if is_prime(N - p, 25)]
ok = N % 2 == 0 and is_prime(g) and not bad and is_prime(N - g, 25)
n = len(list(primerange(2, g)))
msg = (f"gmpy2 {gmpy2.version()}, {time.strftime('%Y-%m-%d')}: N is even and has {len(str(N))} digits; g = {g} is prime; "
       f"N - p is composite for all {n} primes p < g (is_prime with 25 rounds returns False, which is definite); "
       f"N - g is a probable prime (25 rounds; its proof is complement_cert.gp). {'OK' if ok else 'FAILED: ' + str(bad[:5])} ({time.time()-t0:.0f}s)")
open(OUT + "/direct_check.log", "w").write(msg + "\n"); print(msg)
EOF
N=$(python3 -c "import json; print(json.load(open('$W/found.json'))['N'])"); GG=$(python3 -c "import json; print(json.load(open('$W/found.json'))['g'])")
cat > $OUT/crosscheck.gp <<EOF
\\\\ Direct PARI check: N - p composite for every prime p < g (ispseudoprime is BPSW; a composite verdict is definite), N - g prime (isprime proves it).
default(parisize, 256000000);
N = $N; g = $GG;
c = 0; forprime(p = 2, g - 1, if(ispseudoprime(N - p), error("N - p prime at p = ", p)); c++);
print("primes p < g checked: ", c, "; isprime(g) = ", isprime(g), "; isprime(N - g) = ", isprime(N - g), "; N even: ", N % 2 == 0, "; digits: ", #Str(N));
EOF
gp -q $OUT/crosscheck.gp < /dev/null > $OUT/crosscheck.log 2>&1; cat $OUT/crosscheck.log
cd $OUT && sha256sum record.json evidence.json complement_cert.gp check_cert.log ecpp_check.log N_minus_g.txt package_stdlib.json verify_stdlib.log direct_check.log crosscheck.gp crosscheck.log > MANIFEST.sha256
echo "[cert] done: $OUT"; ls -la $OUT
